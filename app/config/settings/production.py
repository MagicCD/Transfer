#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生产环境配置模块
包含生产环境特定的配置项

注意：此文件只包含与配置模板中的默认值不同的配置项
其他配置项将从配置模板中加载
"""

import os

# 调试模式
DEBUG = False

# 临时文件最长保存时间 - 生产环境保留更长时间
TEMP_FILES_MAX_AGE = int(os.getenv('TEMP_FILES_MAX_AGE', 24))  # 小时

# 缓存配置 - 生产环境缓存更长时间
FILES_CACHE_TTL = int(os.getenv('FILES_CACHE_TTL', 30))  # 秒

# 安全配置
SECURE_COOKIES = os.getenv('SECURE_COOKIES', 'True').lower() in ['true', '1', 'yes']  # 生产环境启用安全Cookie
