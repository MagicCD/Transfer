#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
上传服务模块
负责文件上传相关的操作，如保存文件、分块上传等
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Tuple, Dict, Any, Optional, Union, BinaryIO

from app.config import UPLOAD_FOLDER, TEMP_CHUNKS_DIR, UPLOAD_STATUS, CHUNKED_UPLOAD_THRESHOLD
from app.core.upload_manager import upload_states
from app.services.file.file_service import remove_partial_file, merge_chunks_async
from app.services.cache.cache_service import invalidate_files_cache
from app.core.exceptions import FileUploadError, ChunkUploadError

# 创建日志对象
logger = logging.getLogger(__name__)

class UploadService:
    """上传服务类，处理文件上传相关操作"""

    @staticmethod
    def save_file(file: BinaryIO, filename: str) -> bool:
        """保存小文件（非分块上传）

        Args:
            file: 文件对象
            filename: 文件名

        Returns:
            是否成功保存

        Raises:
            FileUploadError: 当保存文件失败时
        """
        try:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # 初始化上传状态
            upload_states[filename] = {
                'status': UPLOAD_STATUS['COMPLETED'],
                'last_chunk': 0,
                'timestamp': datetime.now()
            }

            # 手动使缓存失效
            invalidate_files_cache()

            logger.info(f"文件保存成功: {filename}")
            return True
        except Exception as e:
            error_msg = f"保存文件时出错: {str(e)}"
            logger.error(error_msg)
            raise FileUploadError(error_msg)

    @staticmethod
    def check_file_size(file: BinaryIO) -> Tuple[int, bool]:
        """检查文件大小，判断是否需要分块上传

        Args:
            file: 文件对象

        Returns:
            tuple: (文件大小, 是否需要分块上传)
        """
        # 获取文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # 重置文件指针到开始位置

        # 检查文件大小，如果大于阈值，需要使用分块上传
        need_chunked_upload = file_size >= CHUNKED_UPLOAD_THRESHOLD

        return file_size, need_chunked_upload

    @staticmethod
    async def process_upload_chunk(filename: str, chunk_number: int, total_chunks: int, chunk_data: bytes) -> Tuple[bool, Dict[str, Any]]:
        """处理上传的文件块

        Args:
            filename: 文件名
            chunk_number: 块编号
            total_chunks: 总块数
            chunk_data: 块数据

        Returns:
            tuple: (是否成功, 状态信息)

        Raises:
            ChunkUploadError: 当块上传失败时
        """
        try:
            from app.core.upload_manager import UploadManager
            return await UploadManager.process_chunk_upload(filename, chunk_number, total_chunks, chunk_data)
        except Exception as e:
            error_msg = f"处理文件块上传时出错: {str(e)}"
            logger.error(error_msg)
            raise ChunkUploadError(message=error_msg, chunk_number=chunk_number, filename=filename)
