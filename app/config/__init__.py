#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块初始化
此模块已移动到app.core.config
为了向后兼容，保留此模块并重定向导入
"""

import sys
import logging
import warnings

# 发出警告
warnings.warn(
    "app.config模块已移动到app.core.config，请更新您的导入语句",
    DeprecationWarning,
    stacklevel=2
)

# 从新位置导入所有内容
from app.core.config import *

# 为了向后兼容，导入配置模型
from app.core.config.config_models import (
    BaseConfig, DevelopmentConfig, ProductionConfig, TestConfig,
    CONFIG_MODELS, get_config_model
)
