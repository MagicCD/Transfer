#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一错误处理模块
提供全局错误处理机制和辅助函数
"""

import logging
import traceback
from functools import wraps
from flask import jsonify, current_app

from app.core.exceptions.base import FileTransferError

# 创建日志对象
logger = logging.getLogger(__name__)

def handle_error(error):
    """处理异常并返回适当的JSON响应
    
    Args:
        error: 捕获的异常
        
    Returns:
        tuple: (JSON响应, HTTP状态码)
    """
    # 如果是自定义异常，使用其定义的状态码和消息
    if isinstance(error, FileTransferError):
        logger.error(f"应用异常: {error.message}")
        response = {
            'success': False,
            'error': error.message
        }
        return jsonify(response), error.code
    
    # 处理其他异常
    logger.error(f"未处理的异常: {str(error)}")
    logger.error(traceback.format_exc())
    
    # 在开发环境中返回详细错误信息
    if current_app.config.get('DEBUG', False):
        response = {
            'success': False,
            'error': str(error),
            'traceback': traceback.format_exc()
        }
    else:
        # 在生产环境中返回通用错误消息
        response = {
            'success': False,
            'error': '服务器内部错误'
        }
    
    return jsonify(response), 500

def api_error_handler(f):
    """API错误处理装饰器
    
    用于包装API路由函数，统一处理异常
    
    Args:
        f: 要装饰的函数
        
    Returns:
        function: 装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return handle_error(e)
    return decorated_function

def register_error_handlers(app):
    """注册全局错误处理器
    
    Args:
        app: Flask应用实例
    """
    # 注册自定义异常处理
    @app.errorhandler(FileTransferError)
    def handle_file_transfer_error(error):
        return handle_error(error)
    
    # 注册HTTP 404错误处理
    @app.errorhandler(404)
    def handle_not_found_error(error):
        response = {
            'success': False,
            'error': '请求的资源不存在'
        }
        return jsonify(response), 404
    
    # 注册HTTP 405错误处理
    @app.errorhandler(405)
    def handle_method_not_allowed_error(error):
        response = {
            'success': False,
            'error': '不支持的请求方法'
        }
        return jsonify(response), 405
    
    # 注册HTTP 413错误处理
    @app.errorhandler(413)
    def handle_request_entity_too_large_error(error):
        response = {
            'success': False,
            'error': '文件太大。请使用浏览器访问此服务进行上传，或者使用分块上传功能。'
        }
        return jsonify(response), 413
    
    # 注册通用异常处理
    @app.errorhandler(Exception)
    def handle_exception(error):
        return handle_error(error)
