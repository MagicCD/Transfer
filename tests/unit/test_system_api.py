#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统API单元测试
"""

import pytest

class TestSystemAPI:
    """系统API测试类"""

    def test_config_manager(self):
        """测试配置管理器"""
        from app.core.config.config_manager import ConfigManager
        config_manager = ConfigManager(env='test')
        assert config_manager.env == 'test'
        assert config_manager.get('DEBUG') is True
        assert config_manager.get('LOG_LEVEL') == 'DEBUG'
        assert 'SECRET_KEY' in config_manager

    def test_config_models(self):
        """测试配置模型"""
        from app.core.config.config_models import get_config_model
        config_model = get_config_model('test')
        assert config_model.DEBUG is True
        assert config_model.LOG_LEVEL == 'DEBUG'
        assert hasattr(config_model, 'SECRET_KEY')


if __name__ == '__main__':
    pytest.main(['-v', __file__])
