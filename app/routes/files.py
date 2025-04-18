#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import os
from flask import jsonify, send_from_directory, request

from app.services.file.storage import StorageService
from app.services.file.metadata import MetadataService
from app.services.cache.cache_service import get_files_info
from app.core.error_handler import api_error_handler
from app.core.exceptions import FileNotFoundError, FileDeleteError

# 创建日志对象
logger = logging.getLogger(__name__)

def register_routes(app, socketio):
    """注册文件相关路由

    Args:
        app: Flask应用实例
        socketio: Socket.IO实例
    """

    @app.route('/files', methods=['GET'])
    @api_error_handler
    def get_files():
        """返回所有文件的信息"""
        # 检查是否需要强制刷新
        force_refresh = request.args.get('force_refresh', '').lower() in ['true', '1', 'yes']

        # 获取文件列表
        files = get_files_info(force_refresh=force_refresh)

        # 返回文件列表
        return jsonify({
            'success': True,
            'files': files,
            'cache_time': time.time(),
            'current_time': time.time(),
            'cache_ttl': 5  # 缓存有效期（秒）
        })

    @app.route('/download/<filename>')
    @api_error_handler
    def download_file(filename):
        """下载文件"""
        # 验证文件是否存在
        file_path = StorageService.get_file_path(filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(filename)

        # 从上传目录发送文件
        from app.core.config import UPLOAD_FOLDER
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

    @app.route('/delete/<filename>', methods=['DELETE'])
    @api_error_handler
    def delete_file(filename):
        """删除单个文件"""
        # 使用StorageService删除文件
        StorageService.delete_file(filename)

        # 获取最新的文件列表
        files = get_files_info(force_refresh=True)

        # 通知所有客户端文件已更新
        socketio.emit('files_updated', {'files': files})

        return jsonify(success=True)

    @app.route('/delete_all', methods=['DELETE'])
    @api_error_handler
    def delete_all_files():
        """删除所有文件"""
        # 使用StorageService删除所有文件
        success, deleted_count = StorageService.delete_all_files()

        # 获取最新的文件列表
        files = get_files_info(force_refresh=True)

        # 通知所有客户端文件已更新
        socketio.emit('files_updated', {'files': files})

        return jsonify(success=True, deleted_count=deleted_count)

    # Socket.IO 事件处理
    @socketio.on('connect')
    def handle_connect():
        # 连接时发送最新的文件列表，强制刷新缓存
        socketio.emit('files_updated', {'files': get_files_info(force_refresh=True)})

    @socketio.on('upload_progress')
    def handle_upload_progress(data):
        socketio.emit('upload_progress_update', data, to=None)
