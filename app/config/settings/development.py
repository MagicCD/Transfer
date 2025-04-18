#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
开发环境配置模块
包含开发环境特定的配置项

注意：此文件只包含与配置模板中的默认值不同的配置项
其他配置项将从配置模板中加载
"""

import os

# 调试模式
DEBUG = True

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')  # 开发环境使用详细日志

# 如果需要覆盖配置模板中的其他默认值，可以在此处添加
