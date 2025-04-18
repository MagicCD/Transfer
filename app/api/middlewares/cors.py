#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CORS中间件模块
处理跨域资源共享
"""

from flask import request, make_response, current_app


def setup_cors(app):
    """设置CORS中间件
    
    Args:
        app: Flask应用实例
    """
    @app.after_request
    def add_cors_headers(response):
        """添加CORS头部
        
        Args:
            response: Flask响应对象
            
        Returns:
            response: 添加了CORS头部的响应对象
        """
        # 允许的域名
        allowed_origins = current_app.config.get('CORS_ALLOWED_ORIGINS', '*')
        origin = request.headers.get('Origin', '')
        
        # 如果请求的域名在允许列表中，或者允许所有域名
        if allowed_origins == '*' or origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin or '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response
    
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path):
        """处理OPTIONS请求
        
        Args:
            path: 请求路径
            
        Returns:
            response: 空响应，带有CORS头部
        """
        response = make_response()
        
        # 允许的域名
        allowed_origins = current_app.config.get('CORS_ALLOWED_ORIGINS', '*')
        origin = request.headers.get('Origin', '')
        
        # 如果请求的域名在允许列表中，或者允许所有域名
        if allowed_origins == '*' or origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin or '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response
