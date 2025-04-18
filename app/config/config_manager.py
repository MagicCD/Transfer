#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器模块
此模块已移动到app.core.config.config_manager
为了向后兼容，保留此模块并重定向导入
"""

import warnings

# 发出警告
warnings.warn(
    "app.config.config_manager模块已移动到app.core.config.config_manager，请更新您的导入语句",
    DeprecationWarning,
    stacklevel=2
)

# 从新位置导入所有内容
from app.core.config.config_manager import ConfigManager
