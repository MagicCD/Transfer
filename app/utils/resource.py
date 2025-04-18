#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

# 创建日志对象
logger = logging.getLogger(__name__)

# 设置日志级别，默认只显示错误信息
logger.setLevel(logging.ERROR)

# 路径缓存字典
_path_cache = {}

def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和PyInstaller打包后的环境
    优化版本：添加了路径缓存和错误处理
    """
    # 检查缓存
    if relative_path in _path_cache:
        return _path_cache[relative_path]

    try:
        # 确定基础路径
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath(".")
        logger.debug(f"Using base path: {base_path}")

        # 生成完整路径
        full_path = os.path.join(base_path, relative_path)

        # 将路径存入缓存
        _path_cache[relative_path] = full_path

        return full_path
    except Exception as e:
        # 发生错误时，记录错误并返回原始路径
        logger.error(f"Error resolving resource path '{relative_path}': {str(e)}")
        # 尝试返回一个合理的默认值
        fallback_path = os.path.join(os.path.abspath("."), relative_path)
        _path_cache[relative_path] = fallback_path
        return fallback_path

# 清除路径缓存
def clear_path_cache():
    """清除路径缓存字典"""
    global _path_cache
    cache_size = len(_path_cache)
    _path_cache.clear()
    logger.debug(f"Resource path cache cleared: {cache_size} items")

# 检查资源路径是否存在
def resource_exists(relative_path):
    """检查相对资源路径是否存在"""
    path = resource_path(relative_path)
    return os.path.exists(path)
