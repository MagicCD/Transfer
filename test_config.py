#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置测试脚本
用于验证配置系统是否正常工作
"""

import os
import sys
import logging

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['SERVER_PORT'] = '8080'
os.environ['UPLOAD_FOLDER'] = 'test_uploads'
os.environ['TEMP_CHUNKS_DIR'] = 'test_uploads/.temp_chunks'

# 导入配置管理器
from app.config.models import BaseConfig, DevelopmentConfig
from app.config.config_manager import ConfigManager

# 创建配置管理器实例
config = ConfigManager()

# 获取配置字典
config_dict = config.get_config()

# 打印配置信息
print("=" * 50)
print("配置测试")
print("=" * 50)
print(f"运行模式: {config['RUNNING_MODE']}")
print(f"应用路径: {config['APPLICATION_PATH']}")
print(f"密钥: {config['SECRET_KEY']}")
print(f"服务器端口: {config['SERVER_PORT']}")
print(f"上传目录: {config['UPLOAD_FOLDER']}")
print(f"临时分块目录: {config['TEMP_CHUNKS_DIR']}")
print(f"日志级别: {config['LOG_LEVEL']}")
print("=" * 50)

# 验证环境变量是否正确加载
assert config['SECRET_KEY'] == 'test-secret-key', "环境变量未正确加载"
assert config['SERVER_PORT'] == 8080, "环境变量未正确转换为整数"
assert config['RUNNING_MODE'] == 'development', "运行模式未正确设置"

# 测试 Pydantic 模型验证
print("\n测试 Pydantic 模型验证:")

# 测试值范围验证
print("\n1. 测试值范围验证:")
try:
    # 创建一个配置模型实例，设置一个无效的端口号
    invalid_config = DevelopmentConfig(SERVER_PORT=80)
    print("❌ 值范围验证失败: 应该检测到无效的端口值")
except Exception as e:
    print(f"✅ 值范围验证成功: {str(e)}")

# 测试依赖关系验证
print("\n2. 测试依赖关系验证:")
try:
    # 创建一个配置模型实例，设置违反依赖关系的值
    invalid_config = DevelopmentConfig(
        CHUNK_SIZE=100 * 1024 * 1024,  # 100MB
        CHUNKED_UPLOAD_THRESHOLD=10 * 1024 * 1024  # 10MB
    )
    print("❌ 依赖关系验证失败: 应该检测到分块大小大于阈值")
except Exception as e:
    print(f"✅ 依赖关系验证成功: {str(e)}")

# 测试选项验证
print("\n3. 测试选项验证:")
try:
    # 创建一个配置模型实例，设置一个无效的日志级别
    invalid_config = DevelopmentConfig(LOG_LEVEL="INVALID")
    print("❌ 选项验证失败: 应该检测到无效的日志级别")
except Exception as e:
    print(f"✅ 选项验证成功: {str(e)}")

print("\n配置测试通过!")
