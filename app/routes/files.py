#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import time
from flask import jsonify, send_from_directory, abort, request

from app.config import UPLOAD_FOLDER
from app.services.cache_service import get_files_info, invalidate_files_cache

# 创建日志对象
logger = logging.getLogger(__name__)

def register_routes(app, socketio):
    """注册文件相关路由
    
    Args:
        app: Flask应用实例
        socketio: Socket.IO实例
    """
    
    @app.route('/files', methods=['GET'])
    def get_files():
        """返回所有文件的信息"""
        try:
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
        except Exception as e:
            logger.error(f"获取文件列表时出错: {str(e)}")
            return jsonify(success=False, error=str(e))
    
    @app.route('/download/<filename>')
    def download_file(filename):
        """下载文件"""
        try:
            return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
        except Exception:
            abort(404)
    
    @app.route('/delete/<filename>', methods=['DELETE'])
    def delete_file(filename):
        """删除单个文件"""
        try:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                # 删除文件
                os.remove(file_path)

                # 手动使缓存失效
                invalidate_files_cache()

                # 获取最新的文件列表
                files = get_files_info(force_refresh=True)

                # 记录日志
                logger.info(f"文件已删除: {filename}, 当前文件数: {len(files)}")

                # 通知所有客户端文件已更新
                socketio.emit('files_updated', {'files': files})

                return jsonify(success=True)
            else:
                logger.warning(f"尝试删除不存在的文件: {filename}")
                return jsonify(success=False, error='File not found')
        except Exception as e:
            logger.error(f"删除文件时出错: {str(e)}")
            return jsonify(success=False, error=str(e))
    
    @app.route('/delete_all', methods=['DELETE'])
    def delete_all_files():
        """删除所有文件"""
        try:
            # 记录删除前的文件数量
            files_before = len([f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))])

            # 删除所有文件
            deleted_count = 0
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count += 1

            # 手动使缓存失效
            invalidate_files_cache()

            # 获取最新的文件列表
            files = get_files_info(force_refresh=True)

            # 记录日志
            logger.info(f"删除了 {deleted_count} 个文件, 删除前: {files_before}, 删除后: {len(files)}")

            # 通知所有客户端文件已更新
            socketio.emit('files_updated', {'files': files})

            return jsonify(success=True, deleted_count=deleted_count)
        except Exception as e:
            logger.error(f"删除所有文件时出错: {str(e)}")
            return jsonify(success=False, error=str(e))
    
    # Socket.IO 事件处理
    @socketio.on('connect')
    def handle_connect():
        # 连接时发送最新的文件列表，强制刷新缓存
        socketio.emit('files_updated', {'files': get_files_info(force_refresh=True)})
    
    @socketio.on('upload_progress')
    def handle_upload_progress(data):
        socketio.emit('upload_progress_update', data, to=None)
