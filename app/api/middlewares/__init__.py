#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中间件模块
包含所有API中间件
"""

from app.api.middlewares.cors import setup_cors

def setup_middlewares(app):
    """设置所有中间件

    Args:
        app: Flask应用实例
    """
    setup_cors(app)
