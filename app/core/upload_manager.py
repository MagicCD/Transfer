#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import shutil
import hashlib
import asyncio
from datetime import datetime

from app.config import (
    UPLOAD_FOLDER, TEMP_CHUNKS_DIR, UPLOAD_STATUS
)
from app.services.file.file_service import (
    remove_partial_file, merge_chunks_async, calculate_chunk_hash, get_chunk_filename
)
from app.services.cache.cache_service import invalidate_files_cache

# 创建日志对象
logger = logging.getLogger(__name__)

# 使用字典存储上传状态信息
# {filename: {
#     'status': UPLOAD_STATUS['UPLOADING'],  # 当前状态
#     'last_chunk': 12,                      # 最后上传的块索引
#     'total_chunks': 100,                   # 总块数
#     'timestamp': datetime.now(),           # 最后更新时间
#     'error': None,                         # 错误信息
#     'uploaded_chunks': set(),              # 已上传的块集合
#     'failed_chunks': set()                 # 上传失败的块集合
# }}
upload_states = {}

class UploadManager:
    """上传管理核心类，处理文件上传相关操作"""
    
    @staticmethod
    def get_upload_state(filename):
        """获取文件上传状态
        
        Args:
            filename (str): 文件名
            
        Returns:
            dict: 上传状态信息
        """
        # 获取文件的状态
        file_state = upload_states.get(filename, {})
        if not file_state:
            return {
                'success': True,
                'status': UPLOAD_STATUS['COMPLETED'],  # 默认完成状态
                'paused': False,
                'last_chunk': 0,
                'total_chunks': 0,
                'upload_in_progress': False,
                'error': None
            }

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
        return {
            'success': True,
            'status': current_status,
            'paused': (current_status == UPLOAD_STATUS['PAUSED']),
            'last_chunk': file_state.get('last_chunk', 0),
            'total_chunks': total_chunks,
            'uploaded_chunks': uploaded_chunks,
            'progress': progress,
            'upload_in_progress': upload_in_progress,
            'error': file_state.get('error'),
            'failed_chunks': list(file_state.get('failed_chunks', set())),
            'timestamp': file_state.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S') if 'timestamp' in file_state else None
        }
    
    @staticmethod
    def pause_upload(filename, chunk_index=0):
        """暂停文件上传
        
        Args:
            filename (str): 文件名
            chunk_index (int): 当前块索引
            
        Returns:
            bool: 是否成功暂停
        """
        try:
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

            logger.info(f"暂停上传文件: {filename}, 当前块: {chunk_index}")
            return True
        except Exception as e:
            logger.error(f"暂停上传时出错: {str(e)}")
            return False
    
    @staticmethod
    def resume_upload(filename):
        """恢复文件上传
        
        Args:
            filename (str): 文件名
            
        Returns:
            tuple: (是否成功, 恢复信息)
        """
        try:
            # 获取文件的状态
            if filename not in upload_states:
                return False, {'error': 'File not found in upload states'}

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

            logger.info(f"恢复上传文件: {filename}, 从块 {last_chunk} 开始, 是否有临时目录: {has_temp_dir}")
            return True, {
                'message': f'已恢复上传: {filename}',
                'last_chunk': last_chunk,
                'has_temp_dir': has_temp_dir,
                'cleaned_chunks': cleaned_count
            }
        except Exception as e:
            logger.error(f"恢复上传时出错: {str(e)}")
            return False, {'error': str(e)}
    
    @staticmethod
    def cancel_upload(filename):
        """取消文件上传
        
        Args:
            filename (str): 文件名
            
        Returns:
            tuple: (是否成功, 取消信息)
        """
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

            return True, {
                'message': f'已取消上传并清理临时文件: {filename}',
                'cleaned': cleaned_count > 0
            }
        except Exception as e:
            logger.error(f"取消上传时出错: {str(e)}")
            return False, {'error': str(e)}
    
    @staticmethod
    async def process_chunk_upload(filename, chunk_number, total_chunks, chunk_data):
        """处理分块上传
        
        Args:
            filename (str): 文件名
            chunk_number (int): 块编号
            total_chunks (int): 总块数
            chunk_data (bytes): 块数据
            
        Returns:
            tuple: (是否成功, 上传信息)
        """
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
                return False, {'error': 'Upload paused', 'paused': True}

            # 为此文件创建一个唯一目录
            file_temp_dir = os.path.join(TEMP_CHUNKS_DIR, filename)
            os.makedirs(file_temp_dir, exist_ok=True)

            # 计算哈希值
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

                # 合并块
                success = await merge_chunks_async(file_temp_dir, final_path, total_chunks)

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
                    return False, {
                        'error': 'Failed to merge chunks',
                        'merge_failed': True,
                        'missing_chunks': missing_chunks
                    }

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

                return True, {'filename': filename, 'status': 'completed'}

            # 返回块上传成功状态
            return True, {'filename': filename, 'status': 'chunk_uploaded'}

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

            return False, {'error': str(e)}
