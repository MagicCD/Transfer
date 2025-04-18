#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地配置文件
此文件不会被版本控制系统跟踪
"""

# 调试模式
DEBUG = True

# 文件上传配置
# UPLOAD_FOLDER = 'custom/uploads/path'
# TEMP_CHUNKS_DIR = 'custom/temp/chunks/path'
TEMP_FILES_MAX_AGE = 4  # 临时文件最长保存时间(小时)

# 缓存配置
FILES_CACHE_TTL = 10  # 文件列表缓存有效期（秒）

# 日志配置
LOG_LEVEL = 'DEBUG'  # 使用详细日志
