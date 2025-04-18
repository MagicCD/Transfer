#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统相关API
提供系统状态、配置等信息的API接口
"""

import os
import psutil
import platform
from flask import Blueprint, jsonify, current_app
from app.core.config import SERVER_PORT, UPLOAD_FOLDER
from app.utils.ip import get_local_ip

# 创建蓝图
system_bp = Blueprint('system', __name__, url_prefix='/api/v1/system')

@system_bp.route('/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        # 获取系统信息
        system_info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'platform_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'ip': get_local_ip(),
                'port': SERVER_PORT
            }
        }

        return jsonify({
            'status': 'success',
            'data': system_info
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@system_bp.route('/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    try:
        # 获取系统状态
        system_status = {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'is_running': True
        }

        return jsonify({
            'status': 'success',
            'data': system_status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def register_routes(app):
    """注册路由"""
    app.register_blueprint(system_bp)
