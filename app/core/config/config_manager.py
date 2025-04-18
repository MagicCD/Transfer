#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器模块
提供统一的配置加载、验证和访问接口
"""

import os
import sys
import logging
import importlib.util
from typing import Dict, Any, Optional, Set
from dotenv import load_dotenv
from pydantic import ValidationError

# 创建日志对象
logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器类，负责加载、验证和提供配置"""

    def __init__(self, env: str = None):
        """
        初始化配置管理器

        Args:
            env: 环境名称，如果为None则自动检测
        """
        # 加载环境变量（只在此处加载一次）
        load_dotenv()

        # 确定运行环境
        self.env = env or self._detect_environment()

        # 确定应用程序基础路径
        self.application_path = self._detect_application_path()

        # 初始化配置字典
        self._config: Dict[str, Any] = {
            'APPLICATION_PATH': self.application_path,
            'RUNNING_MODE': self.env
        }

        # 加载配置
        self._load_config()

        # 设置日志配置
        self._setup_logging()

        logger.info(f"配置管理器初始化完成，运行环境: {self.env}")

    def _detect_environment(self) -> str:
        """
        检测当前运行环境

        Returns:
            str: 环境名称 (development, production, test)
        """
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe文件
            return "production"
        else:
            # 从环境变量中获取运行模式，默认为开发模式
            return os.getenv('FLASK_ENV', 'development').lower()

    def _load_config(self) -> None:
        """加载配置"""
        try:
            # 导入配置模型
            from app.core.config.config_models import get_config_model, CONFIG_MODELS

            # 1. 获取环境特定的配置模型实例
            config_model = get_config_model(self.env)

            # 2. 从环境变量加载配置
            env_vars = {k: v for k, v in os.environ.items()}

            # 3. 加载本地配置（如果存在）
            local_config = self._load_local_config()

            # 4. 合并配置
            # 先使用环境变量更新配置模型
            config_data = config_model.dict()

            # 更新运行时配置
            config_data.update({
                'APPLICATION_PATH': self.application_path,
                'RUNNING_MODE': self.env
            })

            # 更新环境变量配置
            for key in config_data.keys():
                env_key = key  # 环境变量名与配置项名称相同
                if env_key in env_vars:
                    # 根据配置项类型进行转换
                    value = env_vars[env_key]
                    if isinstance(config_data[key], bool):
                        config_data[key] = value.lower() in ['true', '1', 'yes', 'y']
                    elif isinstance(config_data[key], int):
                        try:
                            config_data[key] = int(value)
                        except ValueError:
                            logger.warning(f"环境变量 {env_key} 的值无法转换为整数: {value}")
                    elif isinstance(config_data[key], float):
                        try:
                            config_data[key] = float(value)
                        except ValueError:
                            logger.warning(f"环境变量 {env_key} 的值无法转换为浮点数: {value}")
                    else:
                        config_data[key] = value

            # 更新本地配置
            if local_config:
                config_data.update(local_config)

            # 5. 创建新的配置模型实例
            try:
                model_class = CONFIG_MODELS.get(self.env, CONFIG_MODELS['base'])
                config_model = model_class(**config_data)

                # 6. 处理路径配置
                config_model.process_paths(self.application_path)

                # 7. 确保必要的目录存在
                config_model.ensure_directories()

                # 8. 更新配置字典
                self._config = config_model.dict()

            except ValidationError as e:
                logger.error(f"配置验证失败: {str(e)}")
                sys.exit(1)

        except ImportError as e:
            logger.error(f"加载配置模型时出错: {str(e)}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"加载配置时出错: {str(e)}")
            sys.exit(1)

    def _detect_application_path(self) -> str:
        """
        检测应用程序基础路径

        Returns:
            str: 应用程序基础路径
        """
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe文件
            return os.path.dirname(sys.executable)
        else:
            # 如果是直接运行的py脚本
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    def _load_local_config(self) -> Optional[Dict[str, Any]]:
        """
        加载本地配置（如果存在）

        Returns:
            Optional[Dict[str, Any]]: 本地配置字典，如果不存在则返回None
        """
        try:
            local_settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'local_settings.py')
            if os.path.exists(local_settings_path):
                spec = importlib.util.spec_from_file_location("local_settings", local_settings_path)
                local_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(local_module)

                # 将本地配置添加到配置字典中
                local_config = {}
                for key in dir(local_module):
                    if not key.startswith('__') and not key.startswith('_'):
                        local_config[key] = getattr(local_module, key)

                logger.debug("本地配置加载成功")
                return local_config
        except Exception as e:
            logger.warning(f"加载本地配置时出错: {str(e)}")
            logger.debug("跳过本地配置加载")

        return None

    def _setup_logging(self) -> None:
        """设置日志配置"""
        if 'LOG_LEVEL' in self._config and 'LOG_FORMAT' in self._config:
            log_level = getattr(logging, self._config['LOG_LEVEL'], logging.INFO)
            logging.basicConfig(
                level=log_level,
                format=self._config['LOG_FORMAT']
            )
            logger.info(f"日志级别设置为: {self._config['LOG_LEVEL']}")

    def get_config(self) -> Dict[str, Any]:
        """
        获取完整的配置字典

        Returns:
            Dict[str, Any]: 配置字典
        """
        return self._config.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取指定配置项的值

        Args:
            key: 配置项名称
            default: 如果配置项不存在，返回的默认值

        Returns:
            Any: 配置项的值或默认值
        """
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """
        通过字典访问语法获取配置项

        Args:
            key: 配置项名称

        Returns:
            Any: 配置项的值

        Raises:
            KeyError: 如果配置项不存在
        """
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        """
        检查配置项是否存在

        Args:
            key: 配置项名称

        Returns:
            bool: 配置项是否存在
        """
        return key in self._config

    def keys(self) -> Set[str]:
        """
        获取所有配置项的名称

        Returns:
            Set[str]: 配置项名称集合
        """
        return set(self._config.keys())

    def items(self):
        """
        获取所有配置项的键值对

        Returns:
            ItemsView: 配置项键值对视图
        """
        return self._config.items()
