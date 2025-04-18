#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器单元测试
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.config.config_manager import ConfigManager
from app.core.config.constants import MB, GB


@pytest.fixture
def config_manager():
    """创建测试用的配置管理器实例"""
    with patch('app.core.config.config_manager.load_dotenv'):
        return ConfigManager(env='test')


class TestConfigManager:
    """配置管理器测试类"""

    def test_init(self, config_manager):
        """测试初始化"""
        assert config_manager.env == 'test'
        assert config_manager.application_path is not None

    def test_detect_environment(self):
        """测试环境检测"""
        with patch('app.core.config.config_manager.load_dotenv'):
            with patch.dict('os.environ', {'FLASK_ENV': 'development'}):
                config_manager = ConfigManager()
                assert config_manager.env == 'development'

            with patch.dict('os.environ', {'FLASK_ENV': 'production'}):
                config_manager = ConfigManager()
                assert config_manager.env == 'production'

            # 测试打包后的环境检测
            with patch('sys.frozen', True, create=True):
                config_manager = ConfigManager()
                assert config_manager.env == 'production'

    def test_get_config(self, config_manager):
        """测试获取配置"""
        config = config_manager.get_config()
        assert isinstance(config, dict)
        assert 'DEBUG' in config
        assert 'LOG_LEVEL' in config
        assert 'SECRET_KEY' in config

    def test_get(self, config_manager):
        """测试获取配置项"""
        assert config_manager.get('DEBUG') is True
        assert config_manager.get('LOG_LEVEL') == 'DEBUG'
        assert config_manager.get('NON_EXISTENT', 'default') == 'default'

    def test_getitem(self, config_manager):
        """测试字典访问语法"""
        assert config_manager['DEBUG'] is True
        assert config_manager['LOG_LEVEL'] == 'DEBUG'
        with pytest.raises(KeyError):
            _ = config_manager['NON_EXISTENT']

    def test_contains(self, config_manager):
        """测试配置项是否存在"""
        assert 'DEBUG' in config_manager
        assert 'LOG_LEVEL' in config_manager
        assert 'NON_EXISTENT' not in config_manager

    def test_keys(self, config_manager):
        """测试获取所有配置项名称"""
        keys = config_manager.keys()
        assert isinstance(keys, set)
        assert 'DEBUG' in keys
        assert 'LOG_LEVEL' in keys

    def test_items(self, config_manager):
        """测试获取所有配置项键值对"""
        items = dict(config_manager.items())
        assert isinstance(items, dict)
        assert items['DEBUG'] is True
        assert items['LOG_LEVEL'] == 'DEBUG'

    def test_load_config_validation(self):
        """测试配置验证"""
        with patch('app.core.config.config_manager.load_dotenv'):
            # 测试配置验证失败
            with patch('app.core.config.config_models.get_config_model') as mock_get_config_model:
                mock_config_model = MagicMock()
                mock_config_model.model_validate.side_effect = Exception('配置验证失败')
                mock_get_config_model.return_value = mock_config_model
                
                with pytest.raises(SystemExit):
                    ConfigManager()

    def test_setup_logging(self, config_manager):
        """测试日志配置"""
        with patch('logging.basicConfig') as mock_basicConfig:
            config_manager._setup_logging()
            mock_basicConfig.assert_called_once()


if __name__ == '__main__':
    pytest.main(['-v', __file__])
