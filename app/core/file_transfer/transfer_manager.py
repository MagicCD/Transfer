#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件传输管理器
负责文件传输的核心功能
"""

import os
import logging
import shutil
import hashlib
from datetime import datetime
from typing import Dict, Any, Tuple, List, Set, Optional, Union

from app.core.config import UPLOAD_FOLDER, TEMP_CHUNKS_DIR, UPLOAD_STATUS
from app.core.exceptions import FileTransferError, FileMergeError, FileNotFoundError
from app.services.file.storage import StorageService
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
upload_states: Dict[str, Dict[str, Any]] = {}

class TransferManager:
    """文件传输管理器，处理文件传输的核心功能"""

    @staticmethod
    def get_upload_state(filename: str) -> Dict[str, Any]:
        """获取文件上传状态

        Args:
            filename: 文件名

        Returns:
            上传状态信息
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

        # 构建返回的状态信息
        return {
            'success': True,
            'status': current_status,
            'paused': current_status == UPLOAD_STATUS['PAUSED'],
            'last_chunk': file_state.get('last_chunk', 0),
            'total_chunks': file_state.get('total_chunks', 0),
            'upload_in_progress': upload_in_progress,
            'error': file_state.get('error', None),
            'uploaded_chunks': list(file_state.get('uploaded_chunks', set())),
            'failed_chunks': list(file_state.get('failed_chunks', set()))
        }

    @staticmethod
    def pause_upload(filename: str, chunk_index: int = 0) -> bool:
        """暂停文件上传

        Args:
            filename: 文件名
            chunk_index: 当前块索引

        Returns:
            是否成功暂停
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
    def resume_upload(filename: str) -> Tuple[bool, Dict[str, Any]]:
        """恢复文件上传

        Args:
            filename: 文件名

        Returns:
            tuple: (是否成功, 恢复信息)
        """
        try:
            # 检查文件状态
            if filename not in upload_states:
                logger.warning(f"尝试恢复不存在的上传: {filename}")
                return False, {'error': 'Upload not found'}

            # 获取文件状态
            file_state = upload_states[filename]
            last_chunk = file_state.get('last_chunk', 0)

            # 检查临时目录是否存在
            file_temp_dir = os.path.join(TEMP_CHUNKS_DIR, filename)
            has_temp_dir = os.path.exists(file_temp_dir)

            # 如果临时目录不存在，创建它
            if not has_temp_dir:
                os.makedirs(file_temp_dir, exist_ok=True)
                logger.info(f"为恢复上传创建临时目录: {file_temp_dir}")

            # 清理损坏的块
            cleaned_count = 0
            if 'failed_chunks' in file_state and file_state['failed_chunks']:
                from app.services.file.storage import clean_corrupted_chunks
                cleaned_count, _ = clean_corrupted_chunks(filename, list(file_state['failed_chunks']))
                # 清除失败块记录
                file_state['failed_chunks'] = set()

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
    def cancel_upload(filename: str) -> Tuple[bool, Dict[str, Any]]:
        """取消文件上传

        Args:
            filename: 文件名

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
    async def process_chunk_upload(filename: str, chunk_number: int, total_chunks: int, chunk_data: bytes) -> Tuple[bool, Dict[str, Any]]:
        """处理分块上传

        Args:
            filename: 文件名
            chunk_number: 块编号
            total_chunks: 总块数
            chunk_data: 块数据

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

            # 创建临时目录
            file_temp_dir = os.path.join(TEMP_CHUNKS_DIR, filename)
            os.makedirs(file_temp_dir, exist_ok=True)

            # 计算块的哈希值
            chunk_hash = hashlib.md5(chunk_data).hexdigest()

            # 生成块文件名
            chunk_filename = f"chunk_{chunk_number}_{chunk_hash}"
            chunk_path = os.path.join(file_temp_dir, chunk_filename)

            # 保存块文件
            with open(chunk_path, 'wb') as f:
                f.write(chunk_data)

            # 更新上传状态
            file_state['last_chunk'] = max(file_state['last_chunk'], chunk_number)
            file_state['timestamp'] = datetime.now()
            file_state['uploaded_chunks'].add(chunk_number)
            if chunk_number in file_state['failed_chunks']:
                file_state['failed_chunks'].remove(chunk_number)

            # 检查是否所有块都已上传
            all_chunks_uploaded = len(file_state['uploaded_chunks']) == total_chunks

            # 如果所有块都已上传，合并文件
            if all_chunks_uploaded:
                logger.info(f"所有块已上传，开始合并文件: {filename}")
                file_state['status'] = UPLOAD_STATUS['MERGING']

                # 合并文件
                final_path = os.path.join(UPLOAD_FOLDER, filename)
                from app.services.file.storage import merge_chunks_async
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

                # 更新状态为已完成
                file_state['status'] = UPLOAD_STATUS['COMPLETED']
                file_state['timestamp'] = datetime.now()

                # 使缓存失效
                invalidate_files_cache()

                logger.info(f"文件上传完成: {filename}")
                return True, {'status': 'completed'}

            # 返回当前状态
            return True, {
                'status': 'chunk_uploaded',
                'chunk': chunk_number,
                'total': total_chunks,
                'progress': len(file_state['uploaded_chunks']) / total_chunks
            }

        except Exception as e:
            logger.error(f"处理分块上传时出错: {str(e)}")

            # 删除部分写入的文件
            final_path = os.path.join(UPLOAD_FOLDER, filename)
            from app.services.file.storage import remove_partial_file
            remove_partial_file(final_path)

            # 更新上传状态，标记错误
            if filename in upload_states:
                upload_states[filename]['status'] = UPLOAD_STATUS['FAILED']
                upload_states[filename]['error'] = str(e)
                upload_states[filename]['timestamp'] = datetime.now()
                if 'failed_chunks' in upload_states[filename] and chunk_number is not None:
                    upload_states[filename]['failed_chunks'].add(chunk_number)

            return False, {'error': str(e)}
