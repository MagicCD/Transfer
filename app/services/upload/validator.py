#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
上传验证服务
负责验证上传请求和文件的有效性
"""

import os
import logging
from typing import Tuple, Dict, Any, Optional, List

from app.core.security.file_validator import FileValidator
from app.core.exceptions import FileUploadError

# 创建日志对象
logger = logging.getLogger(__name__)

class UploadValidatorService:
    """上传验证服务类，处理上传验证相关操作"""
    
    @staticmethod
    def validate_upload_request(filename: str, mime_type: Optional[str] = None) -> Tuple[bool, str]:
        """验证上传请求
        
        Args:
            filename: 文件名
            mime_type: MIME类型（可选）
            
        Returns:
            tuple: (是否有效, 错误信息)
            
        Raises:
            FileUploadError: 当上传请求无效时
        """
        # 验证文件安全性
        is_safe, error_message = FileValidator.validate_file(filename, mime_type)
        if not is_safe:
            logger.warning(f"上传请求验证失败: {error_message}, 文件名: {filename}, MIME类型: {mime_type}")
            raise FileUploadError(error_message)
        
        return True, ""
    
    @staticmethod
    def validate_chunk_request(filename: str, chunk_number: int, total_chunks: int) -> Tuple[bool, str]:
        """验证分块上传请求
        
        Args:
            filename: 文件名
            chunk_number: 块编号
            total_chunks: 总块数
            
        Returns:
            tuple: (是否有效, 错误信息)
            
        Raises:
            FileUploadError: 当分块上传请求无效时
        """
        # 验证文件名
        is_safe, error_message = FileValidator.validate_file(filename)
        if not is_safe:
            logger.warning(f"分块上传请求验证失败: {error_message}, 文件名: {filename}")
            raise FileUploadError(error_message)
        
        # 验证块编号和总块数
        if chunk_number < 0 or chunk_number >= total_chunks:
            error_message = f"无效的块编号: {chunk_number}, 总块数: {total_chunks}"
            logger.warning(f"分块上传请求验证失败: {error_message}")
            raise FileUploadError(error_message)
        
        return True, ""
