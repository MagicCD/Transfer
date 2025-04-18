#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import asyncio
import shutil
from datetime import datetime
from flask import request, jsonify

from app.config import UPLOAD_FOLDER, TEMP_CHUNKS_DIR, UPLOAD_STATUS
from app.services.file_service import (
    upload_states, calculate_chunk_hash, get_chunk_filename, 
    merge_chunks_async, remove_partial_file, clean_corrupted_chunks
)
from app.services.cache_service import get_files_info, invalidate_files_cache

# 创建日志对象
logger = logging.getLogger(__name__)

def register_routes(app, socketio):
    """注册上传相关路由
    
    Args:
        app: Flask应用实例
        socketio: Socket.IO实例
    """
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        """处理普通文件上传"""
        # 检查是否有文件部分
        if 'file' not in request.files:
            return jsonify(success=False, error='No file part')

        file = request.files['file']

        # 如果用户没有选择文件
        if file.filename == '':
            return jsonify(success=False, error='No selected file')

        # 获取文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # 重置文件指针到开始位置

        # 检查文件大小，如果大于50MB，返回需要使用分块上传的提示
        if file_size >= 50 * 1024 * 1024:  # 50MB
            logger.info(f"文件 {file.filename} 大小为 {file_size} 字节，需要使用分块上传")
            return jsonify(
                success=False,
                error='Large file detected',
                use_chunked_upload=True,
                file_size=file_size,
                message='此文件大小超过50MB，需要使用分块上传'
            )

        # 保存文件（小于50MB的文件）
        try:
            filename = os.path.basename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # 初始化上传状态
            upload_states[filename] = {
                'paused': False,
                'last_chunk': 0,
                'timestamp': datetime.now()
            }

            # 手动使缓存失效
            invalidate_files_cache()

            # 通知所有客户端文件已更新
            socketio.emit('files_updated', {'files': get_files_info(force_refresh=True)})

            return jsonify(success=True, filename=filename)
        except Exception as e:
            logger.error(f"上传文件时出错: {str(e)}")
            return jsonify(success=False, error=str(e))
    
    @app.route('/upload/chunk', methods=['POST'])
    def upload_chunk():
        """处理分块上传"""
        # 获取参数
        chunk_number = int(request.form.get('chunk_number', 0))
        total_chunks = int(request.form.get('total_chunks', 0))
        filename = request.form.get('filename', '')

        # 检查参数
        if not filename or 'file' not in request.files:
            return jsonify(success=False, error='Invalid request parameters')

        # 确保文件名安全
        filename = os.path.basename(filename)
        chunk = request.files['file']
        file_temp_dir = None

        try:
            # 初始化上传状态（如果不存在）
            if filename not in upload_states:
                upload_states[filename] = {
                    'status': UPLOAD_STATUS['UPLOADING'],
                    'last_chunk': 0,
                    'total_chunks': total_chunks,
                    'timestamp': datetime.now(),
                    'uploaded_chunks': set(),
                    'failed_chunks': set(),
                    'error': None
                }

            # 获取文件状态
            file_state = upload_states[filename]

            # 检查是否暂停上传
            if file_state['status'] == UPLOAD_STATUS['PAUSED']:
                logger.info(f"文件上传已暂停: {filename}, 当前块: {chunk_number}")
                return jsonify(success=False, error='Upload paused', paused=True)

            # 为此文件创建一个唯一目录
            file_temp_dir = os.path.join(TEMP_CHUNKS_DIR, filename)
            os.makedirs(file_temp_dir, exist_ok=True)

            # 读取块数据并计算哈希值
            chunk_data = chunk.read()
            chunk_hash = calculate_chunk_hash(chunk_data)

            # 生成基于哈希的块文件名
            chunk_filename = get_chunk_filename(chunk_number, chunk_hash)
            chunk_path = os.path.join(file_temp_dir, chunk_filename)

            # 检查该块是否已经上传
            chunk_exists = False
            for existing_file in os.listdir(file_temp_dir):
                if existing_file.startswith(f"chunk_{chunk_number}_"):
                    # 已存在相同块索引的文件
                    existing_path = os.path.join(file_temp_dir, existing_file)
                    existing_hash = existing_file.split('_')[-1] if len(existing_file.split('_')) > 2 else None

                    if existing_hash == chunk_hash:
                        # 相同的哈希值，块已存在
                        chunk_exists = True
                        chunk_path = existing_path
                        logger.info(f"块 {chunk_number} 已存在，哈希值匹配: {chunk_hash}")
                        break
                    else:
                        # 不同的哈希值，删除旧块
                        try:
                            os.remove(existing_path)
                            logger.info(f"删除旧块: {existing_file}, 将替换为新块: {chunk_filename}")
                        except Exception as del_err:
                            logger.error(f"删除旧块时出错: {str(del_err)}")

            # 如果块不存在，则保存
            if not chunk_exists:
                # 将块数据写入文件
                with open(chunk_path, 'wb') as f:
                    f.write(chunk_data)
                logger.info(f"保存块 {chunk_number}/{total_chunks-1}, 哈希值: {chunk_hash}")

            # 更新上传状态
            file_state['last_chunk'] = max(file_state.get('last_chunk', 0), chunk_number + 1)
            file_state['timestamp'] = datetime.now()
            file_state['uploaded_chunks'].add(chunk_number)

            # 如果该块之前在失败列表中，则移除
            if chunk_number in file_state['failed_chunks']:
                file_state['failed_chunks'].remove(chunk_number)

            # 如果这是最后一个块或所有块都已上传，合并所有块
            all_chunks_uploaded = len(file_state['uploaded_chunks']) == total_chunks
            is_last_chunk = chunk_number == total_chunks - 1

            if is_last_chunk or all_chunks_uploaded:
                # 更新状态为合并中
                file_state['status'] = UPLOAD_STATUS['MERGING']

                # 使用异步IO合并块
                final_path = os.path.join(UPLOAD_FOLDER, filename)

                # 使用 asyncio.run() 替代手动管理事件循环
                try:
                    success = asyncio.run(merge_chunks_async(file_temp_dir, final_path, total_chunks))
                except RuntimeError as e:
                    # 处理已有事件循环的情况
                    if "There is no current event loop in thread" in str(e):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        success = loop.run_until_complete(merge_chunks_async(file_temp_dir, final_path, total_chunks))
                        loop.close()
                    else:
                        # 删除部分写入的文件
                        remove_partial_file(final_path)
                        raise

                if not success:
                    # 合并失败，更新状态并记录错误
                    file_state['status'] = UPLOAD_STATUS['FAILED']
                    file_state['error'] = 'Failed to merge chunks'

                    # 检查是否有缺失的块
                    missing_chunks = []
                    for i in range(total_chunks):
                        found = False
                        for existing_file in os.listdir(file_temp_dir):
                            if existing_file.startswith(f"chunk_{i}_"):
                                found = True
                                break
                        if not found:
                            missing_chunks.append(i)
                            file_state['failed_chunks'].add(i)

                    if missing_chunks:
                        logger.warning(f"发现缺失的块: {missing_chunks}")

                    logger.error(f"合并文件块失败: {filename}")
                    return jsonify(
                        success=False,
                        error='Failed to merge chunks',
                        merge_failed=True,
                        missing_chunks=missing_chunks
                    )

                # 合并成功，清理临时文件
                try:
                    shutil.rmtree(file_temp_dir)
                    file_temp_dir = None  # 标记为已清理
                except Exception as e:
                    logger.error(f"清理临时分块目录出错: {str(e)}")

                # 更新状态为完成并从上传状态中移除
                file_state['status'] = UPLOAD_STATUS['COMPLETED']
                # 延迟删除状态，给前端时间查询完成状态
                # 定时清理任务会清理过期的状态

                # 手动使缓存失效
                invalidate_files_cache()

                # 通知所有客户端文件已更新
                socketio.emit('files_updated', {'files': get_files_info(force_refresh=True)})

                return jsonify(success=True, filename=filename, status='completed')

            # 返回块上传成功状态
            return jsonify(success=True, filename=filename, status='chunk_uploaded')

        except Exception as e:
            logger.error(f"处理分块上传时出错: {str(e)}")

            # 删除部分写入的文件
            final_path = os.path.join(UPLOAD_FOLDER, filename)
            remove_partial_file(final_path)

            # 更新上传状态，标记错误
            if filename in upload_states:
                upload_states[filename]['status'] = UPLOAD_STATUS['FAILED']
                upload_states[filename]['error'] = str(e)
                upload_states[filename]['timestamp'] = datetime.now()
                if 'failed_chunks' in upload_states[filename] and chunk_number is not None:
                    upload_states[filename]['failed_chunks'].add(chunk_number)

            return jsonify(success=False, error=str(e))
    
    @app.route('/cancel_upload/<filename>', methods=['POST'])
    def cancel_upload(filename):
        """取消文件上传并清理临时文件"""
        try:
            # 清理临时目录下该文件的分块
            file_temp_dir = os.path.join(TEMP_CHUNKS_DIR, filename)
            cleaned_count = 0

            if os.path.exists(file_temp_dir):
                try:
                    # 删除整个临时目录
                    shutil.rmtree(file_temp_dir)
                    logger.info(f"已删除临时目录: {file_temp_dir}")
                    cleaned_count = 1  # 标记已清理
                except Exception as del_err:
                    logger.error(f"删除临时目录时出错: {str(del_err)}")

            # 更新上传状态
            if filename in upload_states:
                # 如果需要保留状态信息以便前端查询，可以将状态设置为已取消
                # 而不是直接删除状态
                upload_states[filename] = {
                    'status': UPLOAD_STATUS['COMPLETED'],  # 标记为完成状态，便于前端处理
                    'timestamp': datetime.now(),
                    'error': 'Upload cancelled by user',
                    'uploaded_chunks': set(),
                    'failed_chunks': set()
                }

                # 延迟删除状态，定时清理任务会清理过期的状态
                logger.info(f"已将上传状态标记为已取消: {filename}")

            # 通知所有客户端上传状态已更新
            socketio.emit('upload_state_updated', {
                'filename': filename,
                'status': 'cancelled',
                'paused': False
            })

            return jsonify(
                success=True,
                message=f'已取消上传并清理临时文件: {filename}',
                cleaned=cleaned_count > 0
            )
        except Exception as e:
            logger.error(f"取消上传时出错: {str(e)}")
            return jsonify(success=False, error=str(e))
    
    @app.route('/pause_upload/<filename>', methods=['POST'])
    def pause_upload(filename):
        """暂停特定文件上传的API"""
        try:
            # 从请求获取当前块索引
            data = request.get_json() or {}
            chunk_index = data.get('chunk_index', 0)

            # 获取文件的上传状态
            if filename not in upload_states:
                # 创建新的状态记录
                upload_states[filename] = {
                    'status': UPLOAD_STATUS['PAUSED'],
                    'last_chunk': chunk_index,
                    'timestamp': datetime.now(),
                    'uploaded_chunks': set(),
                    'failed_chunks': set(),
                    'error': None
                }
            else:
                # 更新现有状态
                file_state = upload_states[filename]

                # 更新状态
                file_state['status'] = UPLOAD_STATUS['PAUSED']
                file_state['last_chunk'] = max(file_state.get('last_chunk', 0), chunk_index)
                file_state['timestamp'] = datetime.now()

            # 通知所有客户端上传状态已更新
            socketio.emit('upload_state_updated', {
                'filename': filename,
                'status': UPLOAD_STATUS['PAUSED'],
                'chunk_index': chunk_index,
                'paused': True
            })

            logger.info(f"暂停上传文件: {filename}, 当前块: {chunk_index}")
            return jsonify(success=True, message=f'已暂停上传: {filename}')
        except Exception as e:
            logger.error(f"暂停上传时出错: {str(e)}")
            return jsonify(success=False, error=str(e))
    
    @app.route('/resume_upload/<filename>', methods=['POST'])
    def resume_upload(filename):
        """恢复特定文件上传的API"""
        try:
            # 获取文件的状态
            if filename not in upload_states:
                return jsonify(success=False, error='File not found in upload states')

            file_state = upload_states[filename]
            last_chunk = file_state.get('last_chunk', 0)
            current_status = file_state.get('status')

            # 检查是否有临时目录
            file_temp_dir = os.path.join(TEMP_CHUNKS_DIR, filename)
            has_temp_dir = os.path.exists(file_temp_dir)

            # 如果当前状态是失败，检查并清理失败的块
            cleaned_count = 0
            if current_status == UPLOAD_STATUS['FAILED'] and has_temp_dir:
                failed_chunks = list(file_state.get('failed_chunks', set()))
                if failed_chunks:
                    # 删除失败的块文件，以便重新上传
                    for chunk_index in failed_chunks:
                        # 删除对应块索引的所有文件
                        for filename_in_dir in os.listdir(file_temp_dir):
                            if filename_in_dir.startswith(f"chunk_{chunk_index}_"):
                                try:
                                    os.remove(os.path.join(file_temp_dir, filename_in_dir))
                                    cleaned_count += 1
                                    logger.info(f"删除失败的块文件: {filename_in_dir}")
                                except Exception as del_err:
                                    logger.error(f"删除失败块时出错: {str(del_err)}")

                    # 清空失败块集合
                    file_state['failed_chunks'] = set()
                    logger.info(f"已清理 {cleaned_count} 个失败块，准备重新上传")

            # 更新状态为上传中
            file_state['status'] = UPLOAD_STATUS['UPLOADING']
            file_state['timestamp'] = datetime.now()
            file_state['error'] = None  # 清除错误信息

            # 通知所有客户端上传状态已更新
            socketio.emit('upload_state_updated', {
                'filename': filename,
                'status': UPLOAD_STATUS['UPLOADING'],
                'chunk_index': last_chunk,
                'paused': False,
                'has_temp_dir': has_temp_dir
            })

            logger.info(f"恢复上传文件: {filename}, 从块 {last_chunk} 开始, 是否有临时目录: {has_temp_dir}")
            return jsonify(
                success=True,
                message=f'已恢复上传: {filename}',
                last_chunk=last_chunk,
                has_temp_dir=has_temp_dir,
                cleaned_chunks=cleaned_count
            )
        except Exception as e:
            logger.error(f"恢复上传时出错: {str(e)}")
            return jsonify(success=False, error=str(e))
    
    @app.route('/upload_state/<filename>', methods=['GET'])
    def get_upload_state(filename):
        """获取文件上传状态的API"""
        try:
            # 获取文件的状态
            file_state = upload_states.get(filename, {})
            if not file_state:
                return jsonify(
                    success=True,
                    status=UPLOAD_STATUS['COMPLETED'],  # 默认完成状态
                    paused=False,
                    last_chunk=0,
                    total_chunks=0,
                    upload_in_progress=False,
                    error=None
                )

            # 检查是否有临时目录，判断上传是否正在进行
            file_temp_dir = os.path.join(TEMP_CHUNKS_DIR, filename)
            upload_in_progress = os.path.exists(file_temp_dir)

            # 获取当前状态
            current_status = file_state.get('status', UPLOAD_STATUS['COMPLETED'])

            # 如果没有临时目录但状态不是完成，可能是已完成或已取消
            if not upload_in_progress and current_status not in [UPLOAD_STATUS['COMPLETED'], UPLOAD_STATUS['PAUSED']]:
                current_status = UPLOAD_STATUS['COMPLETED']

            # 计算上传进度
            total_chunks = file_state.get('total_chunks', 0)
            uploaded_chunks = len(file_state.get('uploaded_chunks', set()))
            progress = 0
            if total_chunks > 0:
                progress = int((uploaded_chunks / total_chunks) * 100)

            # 返回更完整的状态信息
            return jsonify(
                success=True,
                status=current_status,
                paused=(current_status == UPLOAD_STATUS['PAUSED']),
                last_chunk=file_state.get('last_chunk', 0),
                total_chunks=total_chunks,
                uploaded_chunks=uploaded_chunks,
                progress=progress,
                upload_in_progress=upload_in_progress,
                error=file_state.get('error'),
                failed_chunks=list(file_state.get('failed_chunks', set())),
                timestamp=file_state.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S') if 'timestamp' in file_state else None
            )
        except Exception as e:
            logger.error(f"获取上传状态时出错: {str(e)}")
            return jsonify(success=False, error=str(e))
