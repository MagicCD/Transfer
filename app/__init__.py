#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import threading
import time
import schedule
from flask import Flask, render_template
from flask_socketio import SocketIO

from app.utils.resource import resource_path
from app.utils.ip import get_local_ip
from app.config import SECRET_KEY, UPLOAD_FOLDER, TEMP_CHUNKS_DIR
from app.services.file_service import clean_temp_files
from app.services.cache_service import clean_caches, get_files_info

# 创建日志对象
logger = logging.getLogger(__name__)

# 创建退出事件
exit_event = threading.Event()

# 创建应用并使用resource_path处理静态文件和模板路径
def create_app():
    """创建并配置Flask应用

    Returns:
        tuple: (app, socketio) - Flask应用实例和Socket.IO实例
    """
    # 注意：resource_path 用于访问打包到程序内部的资源 (templates, static)
    templates_dir = resource_path('templates')
    static_dir = resource_path('static') if os.path.exists(resource_path('static')) else None

    app = Flask(__name__,
                template_folder=templates_dir,
                static_url_path='/static',
                static_folder=static_dir)

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['TEMP_CHUNKS_DIR'] = TEMP_CHUNKS_DIR

    # 初始化 Socket.IO - 指定async_mode为threading，避免使用eventlet或gevent
    socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*", logger=False, engineio_logger=False)

    # 确保上传目录和临时分块目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(TEMP_CHUNKS_DIR, exist_ok=True)

    # 自定义错误处理
    @app.errorhandler(413)
    def request_entity_too_large(_):
        # 使用下划线作为参数名表示我们不使用这个参数
        return {'success': False, 'error': '文件太大。请使用浏览器访问此服务进行上传，或者使用分块上传功能。'}, 413

    # 注册主页路由
    @app.route('/')
    def index():
        return render_template('index.html',
                            server_ip=get_local_ip(),
                            server_port=5000,
                            files=get_files_info(force_refresh=False))

    # 注册其他路由
    from app.routes import files, upload
    # 注册路由
    files.register_routes(app, socketio)
    upload.register_routes(app, socketio)

    return app, socketio

# 定时任务：清理临时文件和缓存
def start_scheduler():
    """启动定时任务调度器

    Returns:
        threading.Thread: 调度器线程
    """
    # 先执行一次清理，然后再设置定时任务
    clean_temp_files()

    # 设置定时清理任务
    schedule.every(1).hours.do(clean_temp_files)

    # 设置定时清理缓存任务
    # 每6小时清理一次缓存
    schedule.every(6).hours.do(clean_caches)

    # 创建一个守护线程来运行调度器
    def run_scheduler():
        while not exit_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    # 启动调度器线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    logger.info("临时文件清理调度器已启动")
    return scheduler_thread

# 创建应用实例
app, socketio = create_app()