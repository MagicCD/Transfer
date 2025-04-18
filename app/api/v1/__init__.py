#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API v1模块
包含API v1版本的所有路由
"""

from app.api.v1 import files, upload

def register_routes(app, socketio):
    """注册API v1版本的所有路由

    Args:
        app: Flask应用实例
        socketio: Socket.IO实例
    """
    files.register_routes(app, socketio)
    upload.register_routes(app, socketio)
