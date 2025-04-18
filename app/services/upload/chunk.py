#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分块上传服务
负责处理文件的分块上传
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, Union, BinaryIO

from app.config import UPLOAD_FOLDER, TEMP_CHUNKS_DIR, UPLOAD_STATUS, CHUNKED_UPLOAD_THRESHOLD
from app.core.file_transfer.transfer_manager import TransferManager
from app.services.cache.cache_service import invalidate_files_cache
from app.core.exceptions import FileUploadError, ChunkUploadError, FileMergeError

# 创建日志对象
logger = logging.getLogger(__name__)

class ChunkUploadService:
    """分块上传服务类，处理文件分块上传相关操作"""
    
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
            from app.core.file_transfer.transfer_manager import upload_states
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
            return await TransferManager.process_chunk_upload(filename, chunk_number, total_chunks, chunk_data)
        except Exception as e:
            error_msg = f"处理文件块上传时出错: {str(e)}"
            logger.error(error_msg)
            raise ChunkUploadError(message=error_msg, chunk_number=chunk_number, filename=filename)
    
    @staticmethod
    def get_upload_state(filename: str) -> Dict[str, Any]:
        """获取文件上传状态
        
        Args:
            filename: 文件名
            
        Returns:
            上传状态信息
        """
        return TransferManager.get_upload_state(filename)
    
    @staticmethod
    def pause_upload(filename: str, chunk_index: int = 0) -> bool:
        """暂停文件上传
        
        Args:
            filename: 文件名
            chunk_index: 当前块索引
            
        Returns:
            是否成功暂停
        """
        return TransferManager.pause_upload(filename, chunk_index)
    
    @staticmethod
    def resume_upload(filename: str) -> Tuple[bool, Dict[str, Any]]:
        """恢复文件上传
        
        Args:
            filename: 文件名
            
        Returns:
            tuple: (是否成功, 恢复信息)
        """
        return TransferManager.resume_upload(filename)
    
    @staticmethod
    def cancel_upload(filename: str) -> Tuple[bool, Dict[str, Any]]:
        """取消文件上传
        
        Args:
            filename: 文件名
            
        Returns:
            tuple: (是否成功, 取消信息)
        """
        return TransferManager.cancel_upload(filename)
