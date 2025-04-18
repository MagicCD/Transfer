#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试环境配置模块
包含测试环境特定的配置项

注意：此文件只包含与配置模板中的默认值不同的配置项
其他配置项将从配置模板中加载
"""

import os
import tempfile

# 调试模式
DEBUG = True

# 使用临时目录作为上传目录
TEMP_DIR = tempfile.mkdtemp()
UPLOAD_FOLDER = os.path.join(TEMP_DIR, 'uploads')
TEMP_CHUNKS_DIR = os.path.join(TEMP_DIR, 'temp_chunks')

# 临时文件和缓存配置
TEMP_FILES_MAX_AGE = 1  # 临时文件最长保存时间(小时)
FILES_CACHE_TTL = 1  # 文件列表缓存有效期（秒）

# 日志配置
LOG_LEVEL = 'DEBUG'  # 测试环境使用详细日志

# 确保测试目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_CHUNKS_DIR, exist_ok=True)
