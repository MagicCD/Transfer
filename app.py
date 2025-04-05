#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import socket
import threading
import logging
import webview

# 导入资源路径辅助函数
from resource_path import resource_path

# 检查 Python 版本兼容性
py_version = sys.version_info
if py_version.major > 3 or (py_version.major == 3 and py_version.minor > 13):
    print("\n警告: 当前 Python 版本为 {}.{}.{}".format(py_version.major, py_version.minor, py_version.micro))
    print("此应用程序在 Python 3.8 至 3.13 版本测试通过，更高版本可能会有兼容性问题。")
    print("尝试继续运行...\n")

from flask import Flask, render_template, request, send_from_directory, jsonify, abort
from flask_socketio import SocketIO

# 创建应用并使用resource_path处理静态文件和模板路径
templates_dir = resource_path('templates')
static_dir = resource_path('static') if os.path.exists(resource_path('static')) else None

app = Flask(__name__, 
            template_folder=templates_dir,
            static_url_path='/static', 
            static_folder=static_dir)

app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = resource_path('uploads')
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB

# 初始化 Socket.IO - 指定async_mode为threading，避免使用eventlet或gevent
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*", logger=False, engineio_logger=False)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 记录服务器状态和全局变量
server_running = False
window = None
server_thread = None
exit_event = threading.Event()

# 获取本机 IP 地址
def get_local_ip():
    try:
        # 创建一个临时套接字连接到一个公共 IP 地址，这样我们可以获取本机在网络中的 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'  # 如果获取失败，返回本地回环地址

# 获取文件图标
def get_file_icon(filename):
    extension = os.path.splitext(filename.lower())[1]
    
    # 图像文件
    if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
        return 'fa-image'
    # 视频文件
    elif extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']:
        return 'fa-video'
    # 音频文件
    elif extension in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a']:
        return 'fa-music'
    # 文档文件
    elif extension in ['.pdf']:
        return 'fa-file-pdf'
    elif extension in ['.doc', '.docx']:
        return 'fa-file-word'
    elif extension in ['.xls', '.xlsx']:
        return 'fa-file-excel'
    elif extension in ['.ppt', '.pptx']:
        return 'fa-file-powerpoint'
    elif extension in ['.txt', '.md', '.rtf']:
        return 'fa-file-alt'
    # 压缩文件
    elif extension in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return 'fa-file-archive'
    # 代码文件
    elif extension in ['.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.php', '.json', '.xml']:
        return 'fa-file-code'
    # 可执行文件
    elif extension in ['.exe', '.msi', '.bat', '.sh']:
        return 'fa-file-invoice'
    # 其他文件
    else:
        return 'fa-file'

# 格式化文件大小
def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

# 获取所有文件信息
def get_files_info():
    files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                files.append({
                    'name': filename,
                    'size': size,
                    'size_formatted': format_file_size(size),
                    'icon': get_file_icon(filename)
                })
    return sorted(files, key=lambda x: x['name'])

# 路由处理

@app.route('/')
def index():
    return render_template('index.html', 
                           server_ip=get_local_ip(), 
                           server_port=5000, 
                           files=get_files_info())

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否有文件部分
    if 'file' not in request.files:
        return jsonify(success=False, error='No file part')
    
    file = request.files['file']
    
    # 如果用户没有选择文件
    if file.filename == '':
        return jsonify(success=False, error='No selected file')
    
    # 保存文件
    try:
        filename = os.path.basename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 通知所有客户端文件已更新
        socketio.emit('files_updated', {'files': get_files_info()})
        
        return jsonify(success=True, filename=filename)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception:
        abort(404)

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            # 通知所有客户端文件已更新
            socketio.emit('files_updated', {'files': get_files_info()})
            return jsonify(success=True)
        else:
            return jsonify(success=False, error='File not found')
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/delete_all', methods=['DELETE'])
def delete_all_files():
    try:
        # 删除所有文件
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # 通知所有客户端文件已更新
        socketio.emit('files_updated', {'files': get_files_info()})
        
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

# Socket.IO 事件处理
@socketio.on('connect')
def handle_connect():
    socketio.emit('files_updated', {'files': get_files_info()})

@socketio.on('upload_progress')
def handle_upload_progress(data):
    socketio.emit('upload_progress_update', data, to=None)

# 只有在直接运行此文件时执行以下代码
# 当从main.py导入时，不会执行这些代码
if __name__ == '__main__':
    # 配置日志级别
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    # 启动服务器线程
    server_thread = threading.Thread(target=lambda: socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True), daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    import time
    time.sleep(2)
    
    # 打包环境中运行时使用webview窗口
    if getattr(sys, 'frozen', False):
        server_url = f"http://{get_local_ip()}:5000"
        window = webview.create_window('内网文件传输工具', server_url, width=900, height=700)
        webview.start(lambda: exit_event.set())
    else:
        # 开发环境下也使用webview窗口
        server_url = f"http://{get_local_ip()}:5000"
        window = webview.create_window('内网文件传输工具', server_url, width=900, height=700)
        webview.start(lambda: exit_event.set()) 