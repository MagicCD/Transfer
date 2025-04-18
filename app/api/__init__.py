#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API模块
包含所有API路由和中间件
"""

from app.api import v1
from app.api.middlewares import setup_middlewares

def init_app(app, socketio):
    """初始化API模块

    Args:
        app: Flask应用实例
        socketio: Socket.IO实例
    """
    # 设置中间件
    setup_middlewares(app)

    # 注册路由
    register_routes(app, socketio)

def register_routes(app, socketio):
    """注册所有API路由

    Args:
        app: Flask应用实例
        socketio: Socket.IO实例
    """
    v1.register_routes(app, socketio)
