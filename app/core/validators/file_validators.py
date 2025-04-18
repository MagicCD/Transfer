#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件验证器模块
提供文件验证相关的功能
"""

import os
import re
import magic
from typing import List, Dict, Any, Optional, BinaryIO, Set, Tuple

from app.config import MAX_CONTENT_LENGTH
from app.core.exceptions import FileUploadError


class FileValidator:
    """文件验证器"""
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """验证文件名是否合法
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否合法
            
        Raises:
            FileUploadError: 文件名不合法
        """
        # 检查文件名是否为空
        if not filename or not filename.strip():
            raise FileUploadError("文件名不能为空")
        
        # 检查文件名长度
        if len(filename) > 255:
            raise FileUploadError("文件名过长，最大长度为255个字符")
        
        # 检查文件名是否包含非法字符
        if re.search(r'[<>:"/\\|?*]', filename):
            raise FileUploadError("文件名包含非法字符 (< > : \" / \\ | ? *)")
        
        # 检查文件名是否以点开头或结尾
        if filename.startswith('.') or filename.endswith('.'):
            raise FileUploadError("文件名不能以点开头或结尾")
        
        return True
    
    @staticmethod
    def validate_file_size(file_obj: BinaryIO) -> bool:
        """验证文件大小是否合法
        
        Args:
            file_obj: 文件对象
            
        Returns:
            bool: 是否合法
            
        Raises:
            FileUploadError: 文件大小不合法
        """
        # 获取文件大小
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)  # 重置文件指针
        
        # 检查文件大小是否超过限制
        if file_size > MAX_CONTENT_LENGTH:
            raise FileUploadError(f"文件大小超过限制，最大允许 {MAX_CONTENT_LENGTH / (1024 * 1024):.2f} MB")
        
        # 检查文件是否为空
        if file_size == 0:
            raise FileUploadError("文件不能为空")
        
        return True
    
    @staticmethod
    def validate_file_type(file_obj: BinaryIO, allowed_types: Optional[List[str]] = None) -> bool:
        """验证文件类型是否合法
        
        Args:
            file_obj: 文件对象
            allowed_types: 允许的MIME类型列表，如果为None则不限制
            
        Returns:
            bool: 是否合法
            
        Raises:
            FileUploadError: 文件类型不合法
        """
        if not allowed_types:
            return True
        
        # 读取文件头部以检测MIME类型
        file_head = file_obj.read(2048)
        file_obj.seek(0)  # 重置文件指针
        
        # 使用python-magic检测MIME类型
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file_head)
        
        # 检查文件类型是否在允许列表中
        if file_type not in allowed_types:
            raise FileUploadError(f"不支持的文件类型: {file_type}，允许的类型: {', '.join(allowed_types)}")
        
        return True
    
    @classmethod
    def validate_file(cls, file_obj: BinaryIO, filename: str, allowed_types: Optional[List[str]] = None) -> bool:
        """验证文件是否合法
        
        Args:
            file_obj: 文件对象
            filename: 文件名
            allowed_types: 允许的MIME类型列表，如果为None则不限制
            
        Returns:
            bool: 是否合法
            
        Raises:
            FileUploadError: 文件不合法
        """
        cls.validate_filename(filename)
        cls.validate_file_size(file_obj)
        cls.validate_file_type(file_obj, allowed_types)
        return True
