#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试配置文件
定义全局测试夹具
"""

import os
import sys
import pytest
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


@pytest.fixture
def app():
    """创建测试用的Flask应用实例"""
    with patch('app.core.config.config_manager.load_dotenv'):
        with patch.dict('os.environ', {'FLASK_ENV': 'test'}):
            app, _ = create_app()
            app.config['TESTING'] = True
            yield app


@pytest.fixture
def client(app):
    """创建测试用的Flask客户端"""
    with app.test_client() as client:
        yield client
