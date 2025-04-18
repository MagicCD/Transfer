#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置定义模块
定义所有配置项及其默认值、验证规则和环境特定值
此文件是配置系统的核心，包含所有配置项的完整定义
"""

from typing import Dict, Any, List, Tuple, Callable, Union, Optional
import os

# 导入常量
from app.config.settings.constants import KB, MB, GB

# =====================================================================
# 配置项定义
# =====================================================================

# 配置项结构：
# {
#     'name': 配置项名称,
#     'type': 配置项类型,
#     'default': 默认值,
#     'env_var': 环境变量名称,
#     'description': 配置项说明,
#     'required': 是否必需,
#     'validation': {  # 可选的验证规则
#         'range': (最小值, 最大值, 错误消息),  # 数值范围验证
#         'options': [可选值列表],  # 枚举值验证
#         'path': 是否验证路径存在,  # 路径验证
#         'create_path': 是否自动创建路径,  # 路径自动创建
#         'dependencies': [  # 依赖关系验证
#             (依赖项名称, 验证函数, 错误消息)
#         ]
#     },
#     'env_values': {  # 环境特定值
#         'development': 开发环境值,
#         'production': 生产环境值,
#         'test': 测试环境值
#     }
# }

CONFIG_DEFINITIONS = [
    # 应用基础配置
    {
        'name': 'SECRET_KEY',
        'type': str,
        'default': 'your-secret-key',
        'env_var': 'SECRET_KEY',
        'description': '应用程序密钥，用于会话加密等安全功能',
        'required': True,
    },
    
    # 服务器配置
    {
        'name': 'SERVER_PORT',
        'type': int,
        'default': 5000,
        'env_var': 'SERVER_PORT',
        'description': '服务器监听端口',
        'required': True,
        'validation': {
            'range': (1024, 65535, "端口号必须在1024-65535之间")
        }
    },
    {
        'name': 'DEBUG',
        'type': bool,
        'default': False,
        'env_var': 'DEBUG',
        'description': '是否启用调试模式',
        'required': False,
        'env_values': {
            'development': True,
            'production': False,
            'test': True
        }
    },
    {
        'name': 'SECURE_COOKIES',
        'type': bool,
        'default': False,
        'env_var': 'SECURE_COOKIES',
        'description': '是否启用安全Cookie（生产环境推荐启用）',
        'required': False,
        'env_values': {
            'production': True
        }
    },
    
    # 文件上传配置
    {
        'name': 'UPLOAD_FOLDER',
        'type': str,
        'default': 'uploads',
        'env_var': 'UPLOAD_FOLDER',
        'description': '上传文件存储目录',
        'required': True,
        'validation': {
            'path': True,
            'create_path': True
        },
        'env_values': {
            'test': lambda: os.path.join(os.environ.get('TEMP_DIR', '/tmp'), 'uploads')
        }
    },
    {
        'name': 'TEMP_CHUNKS_DIR',
        'type': str,
        'default': 'uploads/.temp_chunks',
        'env_var': 'TEMP_CHUNKS_DIR',
        'description': '临时分块文件存储目录',
        'required': True,
        'validation': {
            'path': True,
            'create_path': True
        },
        'env_values': {
            'test': lambda: os.path.join(os.environ.get('TEMP_DIR', '/tmp'), 'temp_chunks')
        }
    },
    {
        'name': 'MAX_CONTENT_LENGTH',
        'type': int,
        'default': 5 * GB,  # 5GB
        'env_var': 'MAX_CONTENT_LENGTH',
        'description': '最大上传文件大小（字节）',
        'required': True,
        'validation': {
            'range': (1 * MB, 10 * GB, "最大内容长度必须在1MB-10GB之间")
        }
    },
    {
        'name': 'CHUNK_SIZE',
        'type': int,
        'default': 5 * MB,  # 5MB
        'env_var': 'CHUNK_SIZE',
        'description': '文件分块大小（字节）',
        'required': True,
        'validation': {
            'range': (1 * MB, 100 * MB, "分块大小必须在1MB-100MB之间"),
            'dependencies': [
                ('CHUNKED_UPLOAD_THRESHOLD', lambda c, t: c <= t, "分块大小必须小于或等于分块上传阈值")
            ]
        }
    },
    {
        'name': 'CHUNKED_UPLOAD_THRESHOLD',
        'type': int,
        'default': 50 * MB,  # 50MB
        'env_var': 'CHUNKED_UPLOAD_THRESHOLD',
        'description': '启用分块上传的文件大小阈值（字节）',
        'required': True,
        'validation': {
            'range': (1 * MB, 1 * GB, "分块上传阈值必须在1MB-1GB之间"),
            'dependencies': [
                ('MAX_CONTENT_LENGTH', lambda t, m: t <= m, "分块上传阈值必须小于或等于最大内容长度")
            ]
        }
    },
    {
        'name': 'TEMP_FILES_MAX_AGE',
        'type': int,
        'default': 2,  # 2小时
        'env_var': 'TEMP_FILES_MAX_AGE',
        'description': '临时文件最长保存时间（小时）',
        'required': True,
        'validation': {
            'range': (1, 168, "临时文件最大保存时间必须在1-168小时之间")
        },
        'env_values': {
            'development': 2,
            'production': 24,
            'test': 1
        }
    },
    
    # 缓存配置
    {
        'name': 'FILES_CACHE_TTL',
        'type': int,
        'default': 5,  # 5秒
        'env_var': 'FILES_CACHE_TTL',
        'description': '文件列表缓存有效期（秒）',
        'required': True,
        'validation': {
            'range': (1, 3600, "文件缓存TTL必须在1-3600秒之间")
        },
        'env_values': {
            'development': 5,
            'production': 30,
            'test': 1
        }
    },
    
    # 日志配置
    {
        'name': 'LOG_LEVEL',
        'type': str,
        'default': 'INFO',
        'env_var': 'LOG_LEVEL',
        'description': '日志级别',
        'required': True,
        'validation': {
            'options': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        },
        'env_values': {
            'development': 'DEBUG',
            'production': 'INFO',
            'test': 'DEBUG'
        }
    },
    {
        'name': 'LOG_FORMAT',
        'type': str,
        'default': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'env_var': None,  # 不从环境变量加载
        'description': '日志格式',
        'required': True,
    },
]

# =====================================================================
# 辅助函数
# =====================================================================

def get_config_item(name: str) -> Optional[Dict[str, Any]]:
    """
    获取指定名称的配置项定义
    
    Args:
        name: 配置项名称
        
    Returns:
        Optional[Dict[str, Any]]: 配置项定义，如果不存在则返回None
    """
    for item in CONFIG_DEFINITIONS:
        if item['name'] == name:
            return item
    return None

def get_required_config() -> Dict[str, type]:
    """
    获取所有必需的配置项及其类型
    
    Returns:
        Dict[str, type]: 配置项名称和类型的字典
    """
    return {item['name']: item['type'] for item in CONFIG_DEFINITIONS if item.get('required', False)}

def get_optional_config() -> Dict[str, Any]:
    """
    获取所有可选的配置项及其默认值
    
    Returns:
        Dict[str, Any]: 配置项名称和默认值的字典
    """
    return {item['name']: item['default'] for item in CONFIG_DEFINITIONS if not item.get('required', False)}

def get_default_values() -> Dict[str, Any]:
    """
    获取所有配置项的默认值
    
    Returns:
        Dict[str, Any]: 配置项名称和默认值的字典
    """
    return {item['name']: item['default'] for item in CONFIG_DEFINITIONS}

def get_env_specific_values(env: str) -> Dict[str, Any]:
    """
    获取指定环境的特定配置值
    
    Args:
        env: 环境名称 (development, production, test)
        
    Returns:
        Dict[str, Any]: 环境特定配置值的字典
    """
    result = {}
    for item in CONFIG_DEFINITIONS:
        env_values = item.get('env_values', {})
        if env in env_values:
            value = env_values[env]
            # 如果值是一个函数，则调用它获取实际值
            if callable(value):
                value = value()
            result[item['name']] = value
    return result

def get_validation_rules() -> Dict[str, Dict[str, Any]]:
    """
    获取所有配置项的验证规则
    
    Returns:
        Dict[str, Dict[str, Any]]: 配置项名称和验证规则的字典
    """
    result = {}
    for item in CONFIG_DEFINITIONS:
        if 'validation' in item:
            result[item['name']] = item['validation']
    return result

def get_env_vars_mapping() -> Dict[str, str]:
    """
    获取配置项名称到环境变量名称的映射
    
    Returns:
        Dict[str, str]: 配置项名称到环境变量名称的映射
    """
    result = {}
    for item in CONFIG_DEFINITIONS:
        env_var = item.get('env_var')
        if env_var:
            result[item['name']] = env_var
    return result

def get_config_descriptions() -> Dict[str, str]:
    """
    获取所有配置项的描述
    
    Returns:
        Dict[str, str]: 配置项名称和描述的字典
    """
    return {item['name']: item['description'] for item in CONFIG_DEFINITIONS}

def get_config_types() -> Dict[str, type]:
    """
    获取所有配置项的类型
    
    Returns:
        Dict[str, type]: 配置项名称和类型的字典
    """
    return {item['name']: item['type'] for item in CONFIG_DEFINITIONS}
