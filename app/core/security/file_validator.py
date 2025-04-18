#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件安全验证模块
负责验证文件的安全性
"""

import os
import logging
import hashlib
from typing import Tuple, List, Dict, Any, Optional, Set

# 创建日志对象
logger = logging.getLogger(__name__)

# 不安全的文件扩展名
UNSAFE_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.sh', '.php', '.phtml', '.pl', '.cgi',
    '.386', '.dll', '.com', '.torrent', '.app', '.jar', '.pif',
    '.vb', '.vbs', '.js', '.reg', '.asm', '.scr', '.inf', '.vbe',
    '.cpl', '.msc', '.hta', '.msi', '.sys', '.bin', '.ps1', '.gadget'
}

# 不安全的MIME类型
UNSAFE_MIME_TYPES = {
    'application/x-msdownload',
    'application/x-executable',
    'application/x-dosexec',
    'application/x-msdos-program',
    'application/x-msi',
    'application/x-coredump',
    'application/x-shockwave-flash',
    'application/x-silverlight-app',
    'application/x-ms-shortcut'
}

class FileValidator:
    """文件安全验证类"""
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """检查文件名是否安全
        
        Args:
            filename: 文件名
            
        Returns:
            是否安全
        """
        if not filename or '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # 检查文件扩展名
        _, ext = os.path.splitext(filename.lower())
        if ext in UNSAFE_EXTENSIONS:
            logger.warning(f"检测到不安全的文件扩展名: {ext}")
            return False
        
        return True
    
    @staticmethod
    def is_safe_mime_type(mime_type: str) -> bool:
        """检查MIME类型是否安全
        
        Args:
            mime_type: MIME类型
            
        Returns:
            是否安全
        """
        if not mime_type:
            return True  # 如果没有提供MIME类型，默认为安全
        
        if mime_type in UNSAFE_MIME_TYPES:
            logger.warning(f"检测到不安全的MIME类型: {mime_type}")
            return False
        
        return True
    
    @staticmethod
    def validate_file(filename: str, mime_type: Optional[str] = None) -> Tuple[bool, str]:
        """验证文件安全性
        
        Args:
            filename: 文件名
            mime_type: MIME类型（可选）
            
        Returns:
            tuple: (是否安全, 错误信息)
        """
        # 检查文件名
        if not FileValidator.is_safe_filename(filename):
            return False, "不安全的文件名"
        
        # 检查MIME类型
        if mime_type and not FileValidator.is_safe_mime_type(mime_type):
            return False, "不安全的文件类型"
        
        return True, ""
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """计算文件哈希值
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法，默认为md5
            
        Returns:
            哈希值
        """
        if not os.path.exists(file_path):
            return ""
        
        hash_obj = None
        if algorithm.lower() == 'md5':
            hash_obj = hashlib.md5()
        elif algorithm.lower() == 'sha1':
            hash_obj = hashlib.sha1()
        elif algorithm.lower() == 'sha256':
            hash_obj = hashlib.sha256()
        else:
            hash_obj = hashlib.md5()  # 默认使用MD5
        
        # 分块读取文件以处理大文件
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
