#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块初始化
负责加载应用程序的配置并确定运行环境
使用ConfigManager类统一管理配置
"""

import sys
import logging

# 初始化日志对象
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入配置管理器
from app.core.config.config_manager import ConfigManager

# 导入常量
from app.core.config.constants import KB, MB, GB, UPLOAD_STATUS, ICON_MAPPING

# 将常量导出到全局命名空间
__all__ = ['KB', 'MB', 'GB', 'UPLOAD_STATUS', 'ICON_MAPPING']

try:
    # 创建配置管理器实例
    config_manager = ConfigManager()

    # 获取配置字典
    config_dict = config_manager.get_config()

    # 将配置字典中的所有变量添加到当前模块的全局命名空间中
    for key, value in config_dict.items():
        globals()[key] = value

    # 现在可以安全地访问这些变量，因为它们已经在全局命名空间中
    running_mode = config_dict.get('RUNNING_MODE', 'unknown')
    application_path = config_dict.get('APPLICATION_PATH', 'unknown')
    log_level = config_dict.get('LOG_LEVEL', 'INFO')

    logger.info(f"配置加载成功，运行模式: {running_mode}")
    logger.info(f"应用程序路径: {application_path}")
    logger.info(f"日志级别: {log_level}")

except Exception as e:
    logger.error(f"配置初始化失败: {str(e)}")
    sys.exit(1)
