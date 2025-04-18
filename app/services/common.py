#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from app.config import ICON_MAPPING, KB, MB, GB

# 创建日志对象
logger = logging.getLogger(__name__)

# 文件图标缓存字典
file_icon_cache = {}

# 文件大小格式化缓存
file_size_cache = {}

# 获取文件图标 - 优化版本
def get_file_icon(filename):
    """根据文件名获取对应的图标类名
    
    Args:
        filename (str): 文件名
        
    Returns:
        str: Font Awesome图标类名
    """
    # 检查缓存中是否已有此文件的图标
    if filename in file_icon_cache:
        return file_icon_cache[filename]

    filename_lower = filename.lower()

    # 处理复合扩展名
    if filename_lower.endswith('.tar.gz') or filename_lower.endswith('.tar.bz2'):
        icon = 'fa-file-archive'
    else:
        # 处理单一扩展名
        extension = os.path.splitext(filename_lower)[1]
        # 直接从映射中获取图标
        icon = ICON_MAPPING.get(extension, 'fa-file')

    # 将结果存入缓存
    file_icon_cache[filename] = icon
    return icon

# 格式化文件大小
def format_file_size(size_bytes):
    """将字节大小格式化为人类可读的形式
    
    Args:
        size_bytes (int): 文件大小（字节）
        
    Returns:
        str: 格式化后的大小字符串，如"1.5 MB"
    """
    # 检查缓存中是否已有此大小的格式化结果
    if size_bytes in file_size_cache:
        return file_size_cache[size_bytes]

    # 计算格式化结果
    if size_bytes < KB:
        result = f"{size_bytes} B"
    elif size_bytes < MB:
        result = f"{size_bytes / KB:.2f} KB"
    elif size_bytes < GB:
        result = f"{size_bytes / MB:.2f} MB"
    else:
        result = f"{size_bytes / GB:.2f} GB"

    # 将结果存入缓存
    file_size_cache[size_bytes] = result
    return result
