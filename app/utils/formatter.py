#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
格式化工具模块
提供各种格式化功能
"""

from app.config import KB, MB, GB

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化后的文件大小字符串
    """
    if size_bytes < KB:
        return f"{size_bytes} B"
    elif size_bytes < MB:
        return f"{size_bytes / KB:.2f} KB"
    elif size_bytes < GB:
        return f"{size_bytes / MB:.2f} MB"
    else:
        return f"{size_bytes / GB:.2f} GB"
