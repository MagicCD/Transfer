#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
from datetime import datetime
import os
import gc

from app.core.config import FILES_CACHE_TTL, UPLOAD_FOLDER
from app.services.common import get_file_icon, format_file_size, file_icon_cache, file_size_cache

# 创建日志对象
logger = logging.getLogger(__name__)

# 文件信息缓存
files_info_cache = {}
files_info_cache_time = 0
files_info_cache_hits = 0  # 缓存命中次数
files_info_cache_misses = 0  # 缓存未命中次数
files_info_cache_invalidations = 0  # 缓存手动失效次数

# 使缓存失效
def invalidate_files_cache():
    """手动使文件列表缓存失效"""
    global files_info_cache, files_info_cache_time, files_info_cache_invalidations
    files_info_cache = {}
    files_info_cache_time = 0
    files_info_cache_invalidations += 1
    logger.debug(f"文件列表缓存已手动失效, 总失效次数: {files_info_cache_invalidations}")

# 获取所有文件信息
def get_files_info(force_refresh=False):
    """获取所有文件信息，支持缓存

    Args:
        force_refresh (bool): 是否强制刷新缓存

    Returns:
        list: 文件信息列表
    """
    global files_info_cache, files_info_cache_time, files_info_cache_hits, files_info_cache_misses

    # 检查缓存是否有效
    current_time = time.time()
    cache_age = current_time - files_info_cache_time

    # 如果缓存有效且不需要强制刷新，直接返回缓存的数据
    if not force_refresh and files_info_cache and cache_age < FILES_CACHE_TTL:
        files_info_cache_hits += 1
        logger.debug(f"文件列表缓存命中，年龄: {cache_age:.2f}秒, 总命中次数: {files_info_cache_hits}")
        return files_info_cache

    # 缓存未命中或需要强制刷新，重新获取文件列表
    files_info_cache_misses += 1
    if force_refresh:
        logger.debug(f"强制刷新文件列表缓存, 总未命中次数: {files_info_cache_misses}")
    else:
        logger.debug(f"文件列表缓存过期 (年龄: {cache_age:.2f}秒), 总未命中次数: {files_info_cache_misses}")

    files = []
    upload_dir = UPLOAD_FOLDER
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                modified_time = os.path.getmtime(file_path)
                modified_time_str = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')

                files.append({
                    'name': filename,
                    'size': size,
                    'size_formatted': format_file_size(size),
                    'icon': get_file_icon(filename),
                    'modified_time': modified_time_str
                })

    # 更新缓存
    files_info_cache = sorted(files, key=lambda x: x['name'])
    files_info_cache_time = current_time
    logger.debug(f"文件列表缓存已更新, 包含 {len(files)} 个文件")

    return files_info_cache

# 清理内存缓存
def clean_caches():
    """清理所有内存缓存"""
    global file_icon_cache, file_size_cache, files_info_cache, files_info_cache_time
    logger.info("清理内存缓存...")

    # 清理所有缓存
    cache_sizes = {
        '文件图标缓存': len(file_icon_cache),
        '文件大小缓存': len(file_size_cache)
    }

    # 重置所有缓存
    file_icon_cache.clear()
    file_size_cache.clear()
    files_info_cache = {}
    files_info_cache_time = 0

    # 记录清理的缓存大小
    for cache_name, size in cache_sizes.items():
        logger.info(f"已清理{cache_name}: {size} 项")

    # 强制垃圾回收
    gc.collect()
