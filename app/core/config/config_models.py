#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模型模块
使用 Pydantic 定义配置模型，提供类型注解和验证
"""

import os
import sys
import tempfile
from typing import Optional, Dict, Any, Callable, List, Union
from pydantic import BaseModel, Field, validator

# 导入常量
from app.core.config.constants import KB, MB, GB

# 基础配置模型
class BaseConfig(BaseModel):
    """基础配置模型，包含所有环境共享的配置项"""

    # 应用基础配置
    SECRET_KEY: str = Field(
        default="your-secret-key",
        description="应用程序密钥，用于会话加密等安全功能"
    )

    # 服务器配置
    SERVER_PORT: int = Field(
        default=5000,
        ge=1024,
        le=65535,
        description="服务器监听端口"
    )

    DEBUG: bool = Field(
        default=False,
        description="是否启用调试模式"
    )

    SECURE_COOKIES: bool = Field(
        default=False,
        description="是否启用安全Cookie（生产环境推荐启用）"
    )

    # 文件上传配置
    UPLOAD_FOLDER: str = Field(
        default="uploads",
        description="上传文件存储目录"
    )

    TEMP_CHUNKS_DIR: str = Field(
        default="uploads/.temp_chunks",
        description="临时分块文件存储目录"
    )

    MAX_CONTENT_LENGTH: int = Field(
        default=5 * GB,  # 5GB
        ge=1 * MB,
        le=10 * GB,
        description="最大上传文件大小（字节）"
    )

    CHUNK_SIZE: int = Field(
        default=5 * MB,  # 5MB
        ge=1 * MB,
        le=100 * MB,
        description="文件分块大小（字节）"
    )

    CHUNKED_UPLOAD_THRESHOLD: int = Field(
        default=50 * MB,  # 50MB
        ge=1 * MB,
        le=1 * GB,
        description="启用分块上传的文件大小阈值（字节）"
    )

    TEMP_FILES_MAX_AGE: int = Field(
        default=2,  # 2小时
        ge=1,
        le=168,
        description="临时文件最长保存时间（小时）"
    )

    # 缓存配置
    FILES_CACHE_TTL: int = Field(
        default=5,  # 5秒
        ge=1,
        le=3600,
        description="文件列表缓存有效期（秒）"
    )

    # 日志配置
    LOG_LEVEL: str = Field(
        default="INFO",
        description="日志级别"
    )

    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )

    # 运行时配置（不从环境变量加载）
    APPLICATION_PATH: Optional[str] = Field(
        default=None,
        description="应用程序基础路径"
    )

    RUNNING_MODE: Optional[str] = Field(
        default=None,
        description="运行模式"
    )

    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v not in valid_levels:
            raise ValueError(f"无效的日志级别，必须是以下之一: {', '.join(valid_levels)}")
        return v

    @validator('CHUNKED_UPLOAD_THRESHOLD')
    def validate_threshold(cls, v, values):
        """验证分块上传阈值"""
        if 'CHUNK_SIZE' in values and v < values['CHUNK_SIZE']:
            raise ValueError("分块上传阈值必须大于或等于分块大小")
        if 'MAX_CONTENT_LENGTH' in values and v > values['MAX_CONTENT_LENGTH']:
            raise ValueError("分块上传阈值必须小于或等于最大内容长度")
        return v

    @validator('CHUNK_SIZE')
    def validate_chunk_size(cls, v, values):
        """验证分块大小"""
        if 'CHUNKED_UPLOAD_THRESHOLD' in values and v > values['CHUNKED_UPLOAD_THRESHOLD']:
            raise ValueError("分块大小必须小于或等于分块上传阈值")
        return v

    def process_paths(self, application_path: str) -> None:
        """处理路径配置，将相对路径转换为绝对路径"""
        # 处理上传目录和临时分块目录的路径
        for key in ['UPLOAD_FOLDER', 'TEMP_CHUNKS_DIR']:
            path = getattr(self, key)
            if not os.path.isabs(path):
                setattr(self, key, os.path.join(application_path, path))

    def ensure_directories(self) -> None:
        """确保必要的目录存在"""
        for key in ['UPLOAD_FOLDER', 'TEMP_CHUNKS_DIR']:
            path = getattr(self, key)
            os.makedirs(path, exist_ok=True)


# 开发环境配置模型
class DevelopmentConfig(BaseConfig):
    """开发环境配置模型"""

    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    TEMP_FILES_MAX_AGE: int = 2  # 2小时
    FILES_CACHE_TTL: int = 5  # 5秒


# 生产环境配置模型
class ProductionConfig(BaseConfig):
    """生产环境配置模型"""

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    TEMP_FILES_MAX_AGE: int = 24  # 24小时
    FILES_CACHE_TTL: int = 30  # 30秒
    SECURE_COOKIES: bool = True


# 测试环境配置模型
class TestConfig(BaseConfig):
    """测试环境配置模型"""

    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    TEMP_FILES_MAX_AGE: int = 1  # 1小时
    FILES_CACHE_TTL: int = 1  # 1秒

    def __init__(self, **data):
        """初始化测试环境配置"""
        super().__init__(**data)

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 设置上传目录和临时分块目录
        self.UPLOAD_FOLDER = os.path.join(temp_dir, 'uploads')
        self.TEMP_CHUNKS_DIR = os.path.join(temp_dir, 'temp_chunks')

        # 确保目录存在
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.TEMP_CHUNKS_DIR, exist_ok=True)


# 配置模型映射
CONFIG_MODELS = {
    'base': BaseConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig
}


def get_config_model(env: str) -> BaseConfig:
    """
    获取指定环境的配置模型

    Args:
        env: 环境名称 (development, production, test)

    Returns:
        BaseConfig: 配置模型实例
    """
    model_class = CONFIG_MODELS.get(env, CONFIG_MODELS['base'])
    return model_class()


# 为了向后兼容，保留这些类
class Config(BaseConfig):
    """兼容旧版本的配置类"""
    pass
