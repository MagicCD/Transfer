#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import socket
import threading
import logging
import time
import shutil
import webview
import schedule
from datetime import datetime, timedelta

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入资源路径辅助函数
from resource_path import resource_path

# 检查 Python 版本兼容性
py_version = sys.version_info
if py_version.major > 3 or (py_version.major == 3 and py_version.minor > 13):
    logger.warning(f"警告: 当前 Python 版本为 {py_version.major}.{py_version.minor}.{py_version.micro}")
    logger.warning("此应用程序在 Python 3.8 至 3.13 版本测试通过，更高版本可能会有兼容性问题。")
    logger.warning("尝试继续运行...\n")

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
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 5GB
app.config['CHUNK_SIZE'] = 5 * 1024 * 1024  # 5MB
app.config['TEMP_CHUNKS_DIR'] = os.path.join(app.config['UPLOAD_FOLDER'], '.temp_chunks')
app.config['TEMP_FILES_MAX_AGE'] = 2  # 临时文件最长保存时间(小时)

# 初始化 Socket.IO - 指定async_mode为threading，避免使用eventlet或gevent
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*", logger=False, engineio_logger=False)

# 确保上传目录和临时分块目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_CHUNKS_DIR'], exist_ok=True)

# 自定义错误处理
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify(success=False, error='文件太大。请使用浏览器访问此服务进行上传，或者使用分块上传功能。'), 413

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

# 获取文件图标 - 优化版本
def get_file_icon(filename):
    filename_lower = filename.lower()
    
    # 处理复合扩展名
    if filename_lower.endswith('.tar.gz'):
        return 'fa-file-archive'
    elif filename_lower.endswith('.tar.bz2'):
        return 'fa-file-archive'
    
    # 处理单一扩展名
    extension = os.path.splitext(filename_lower)[1]
    
    icon_map = {
        # 图像文件
        '.jpg': 'fa-image', '.jpeg': 'fa-image', '.png': 'fa-image', '.gif': 'fa-image',
        '.bmp': 'fa-image', '.svg': 'fa-image', '.webp': 'fa-image',
        
        # 视频文件
        '.mp4': 'fa-video', '.avi': 'fa-video', '.mov': 'fa-video', '.wmv': 'fa-video',
        '.flv': 'fa-video', '.mkv': 'fa-video', '.webm': 'fa-video',
        
        # 音频文件
        '.mp3': 'fa-music', '.wav': 'fa-music', '.ogg': 'fa-music', '.flac': 'fa-music',
        '.aac': 'fa-music', '.m4a': 'fa-music',
        
        # 文档文件
        '.pdf': 'fa-file-pdf',
        '.doc': 'fa-file-word', '.docx': 'fa-file-word',
        '.xls': 'fa-file-excel', '.xlsx': 'fa-file-excel', '.csv': 'fa-file-excel',
        '.ppt': 'fa-file-powerpoint', '.pptx': 'fa-file-powerpoint',
        '.txt': 'fa-file-alt', '.md': 'fa-file-alt', '.rtf': 'fa-file-alt',
        
        # 压缩文件
        '.zip': 'fa-file-archive', '.rar': 'fa-file-archive', '.7z': 'fa-file-archive',
        '.tar': 'fa-file-archive', '.gz': 'fa-file-archive', '.bz2': 'fa-file-archive',
        
        # 代码文件
        '.html': 'fa-file-code', '.css': 'fa-file-code', '.js': 'fa-file-code',
        '.py': 'fa-file-code', '.java': 'fa-file-code', '.c': 'fa-file-code',
        '.cpp': 'fa-file-code', '.php': 'fa-file-code', '.json': 'fa-file-code',
        '.xml': 'fa-file-code', '.yaml': 'fa-file-code', '.yml': 'fa-file-code',
        
        # 可执行文件
        '.exe': 'fa-file-invoice', '.msi': 'fa-file-invoice',
        '.bat': 'fa-file-invoice', '.sh': 'fa-file-invoice',
    }
    
    return icon_map.get(extension, 'fa-file')  # 返回对应图标或默认图标

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

# 清理过期的临时文件
def clean_temp_files():
    try:
        temp_dir = app.config['TEMP_CHUNKS_DIR']
        if not os.path.exists(temp_dir):
            return
            
        current_time = datetime.now()
        max_age = timedelta(hours=app.config['TEMP_FILES_MAX_AGE'])
        
        # 遍历临时目录中的所有文件
        for dirname in os.listdir(temp_dir):
            dir_path = os.path.join(temp_dir, dirname)
            if not os.path.isdir(dir_path):
                continue
                
            # 获取文件夹的修改时间
            dir_modified_time = datetime.fromtimestamp(os.path.getmtime(dir_path))
            
            # 如果文件夹超过最大保留时间，则删除
            if current_time - dir_modified_time > max_age:
                logger.info(f"清理过期临时分块: {dirname}")
                shutil.rmtree(dir_path)
    except Exception as e:
        logger.error(f"清理临时文件时出错: {str(e)}")
        
    # 清理过期的上传状态信息
    try:
        # 创建要删除的键列表
        keys_to_delete = []
        
        # 检查所有上传状态
        for filename, state in upload_states.items():
            # 获取状态的最后更新时间
            last_update = state.get('timestamp')
            if last_update and (current_time - last_update > max_age):
                keys_to_delete.append(filename)
                
        # 删除过期的状态信息        
        for key in keys_to_delete:
            logger.info(f"清理过期上传状态: {key}")
            upload_states.pop(key, None)
            
    except Exception as e:
        logger.error(f"清理上传状态时出错: {str(e)}")

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
        
        # 初始化上传状态
        upload_states[filename] = {
            'paused': False,
            'last_chunk': 0,
            'timestamp': datetime.now()
        }
        
        # 通知所有客户端文件已更新
        socketio.emit('files_updated', {'files': get_files_info()})
        
        return jsonify(success=True, filename=filename)
    except Exception as e:
        logger.error(f"上传文件时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

@app.route('/upload/chunk', methods=['POST'])
def upload_chunk():
    # 获取参数
    chunk_number = int(request.form.get('chunk_number', 0))
    total_chunks = int(request.form.get('total_chunks', 0))
    filename = request.form.get('filename', '')
    
    # 检查参数
    if not filename or 'file' not in request.files:
        return jsonify(success=False, error='Invalid request parameters')
    
    # 初始化上传状态（如果不存在）
    if filename not in upload_states:
        upload_states[filename] = {
            'paused': False,
            'last_chunk': 0,
            'total_chunks': total_chunks,
            'timestamp': datetime.now()
        }
    
    # 检查是否暂停上传
    file_state = upload_states.get(filename, {})
    if file_state.get('paused', False):
        logger.info(f"文件上传已暂停: {filename}, 当前块: {chunk_number}")
        return jsonify(success=False, error='Upload paused', paused=True)
    
    chunk = request.files['file']
    
    try:
        # 确保文件名安全
        filename = os.path.basename(filename)
        
        # 为此文件创建一个唯一目录
        file_temp_dir = os.path.join(app.config['TEMP_CHUNKS_DIR'], filename)
        os.makedirs(file_temp_dir, exist_ok=True)
        
        # 保存当前块
        chunk_path = os.path.join(file_temp_dir, f"chunk_{chunk_number}")
        chunk.save(chunk_path)
        
        # 如果这是最后一个块，合并所有块
        if chunk_number == total_chunks - 1:
            # 合并块 - 优化版本：流式写入，减少内存占用
            final_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(final_path, 'ab') as outfile:  # 使用追加二进制模式
                for i in range(total_chunks):
                    chunk_file_path = os.path.join(file_temp_dir, f"chunk_{i}")
                    if os.path.exists(chunk_file_path):
                        with open(chunk_file_path, 'rb') as infile:
                            # 逐块读写，减少内存占用
                            while True:
                                data = infile.read(1024*1024)  # 每次读取1MB
                                if not data:
                                    break
                                outfile.write(data)
            
            # 清理临时文件
            try:
                shutil.rmtree(file_temp_dir)
            except Exception as e:
                logger.error(f"清理临时分块目录出错: {str(e)}")
            
            # 从上传状态中移除
            if filename in upload_states:
                del upload_states[filename]
            
            # 通知所有客户端文件已更新
            socketio.emit('files_updated', {'files': get_files_info()})
            
            return jsonify(success=True, filename=filename, status='completed')
        
        # 更新上传状态
        if filename in upload_states:
            upload_states[filename]['last_chunk'] = chunk_number + 1
            upload_states[filename]['timestamp'] = datetime.now()
        
        return jsonify(success=True, filename=filename, status='chunk_uploaded')
    
    except Exception as e:
        logger.error(f"处理分块上传时出错: {str(e)}")
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
        logger.error(f"删除文件时出错: {str(e)}")
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
        logger.error(f"删除所有文件时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

@app.route('/cancel_upload/<filename>', methods=['POST'])
def cancel_upload(filename):
    try:
        # 清理临时目录下该文件的分块
        file_temp_dir = os.path.join(app.config['TEMP_CHUNKS_DIR'], filename)
        if os.path.exists(file_temp_dir):
            shutil.rmtree(file_temp_dir)
            return jsonify(success=True, message=f'已取消上传并清理临时文件: {filename}')

        return jsonify(success=True, message='无需清理临时文件')
    except Exception as e:
        logger.error(f"取消上传时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

# 上传状态管理
# 使用字典存储上传状态信息：{filename: {'paused': True/False, 'last_chunk': 12}}
upload_states = {}

@app.route('/pause_upload/<filename>', methods=['POST'])
def pause_upload(filename):
    """暂停特定文件上传的API"""
    try:
        # 从请求获取当前块索引
        data = request.get_json() or {}
        chunk_index = data.get('chunk_index', 0)
        
        # 记录原始状态
        previous_state = upload_states.get(filename, {})
        previous_chunk = previous_state.get('last_chunk', -1) if previous_state else -1
        
        # 更新文件的暂停状态
        upload_states[filename] = {
            'paused': True,
            'last_chunk': chunk_index,
            'timestamp': datetime.now()
        }
        
        # 通知所有客户端上传状态已更新
        socketio.emit('upload_state_updated', {
            'filename': filename,
            'status': 'paused',
            'chunk_index': chunk_index,
            'paused': True
        })
        
        logger.info(f"暂停上传文件: {filename}, 当前块: {chunk_index}, 之前的块: {previous_chunk}")
        return jsonify(success=True, message=f'已暂停上传: {filename}')
    except Exception as e:
        logger.error(f"暂停上传时出错: {str(e)}")
        return jsonify(success=False, error=str(e))
    
@app.route('/resume_upload/<filename>', methods=['POST'])
def resume_upload(filename):
    """恢复特定文件上传的API"""
    try:
        # 获取文件的暂停状态
        file_state = upload_states.get(filename, {})
        last_chunk = file_state.get('last_chunk', 0)
        was_paused = file_state.get('paused', False)
        
        # 更新状态为非暂停
        if filename in upload_states:
            upload_states[filename]['paused'] = False
            upload_states[filename]['timestamp'] = datetime.now()
        
        # 通知所有客户端上传状态已更新
        socketio.emit('upload_state_updated', {
            'filename': filename,
            'status': 'resumed',
            'chunk_index': last_chunk,
            'paused': False
        })
        
        logger.info(f"恢复上传文件: {filename}, 从块: {last_chunk}, 之前是否暂停: {was_paused}")
        return jsonify(success=True, message=f'已恢复上传: {filename}', last_chunk=last_chunk)
    except Exception as e:
        logger.error(f"恢复上传时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

@app.route('/upload_state/<filename>', methods=['GET'])
def get_upload_state(filename):
    """获取文件上传状态的API"""
    try:
        # 获取文件的暂停状态
        file_state = upload_states.get(filename, {})
        if not file_state:
            return jsonify(success=True, paused=False, last_chunk=0)
            
        return jsonify(
            success=True, 
            paused=file_state.get('paused', False),
            last_chunk=file_state.get('last_chunk', 0)
        )
    except Exception as e:
        logger.error(f"获取上传状态时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

# Socket.IO 事件处理
@socketio.on('connect')
def handle_connect():
    socketio.emit('files_updated', {'files': get_files_info()})

@socketio.on('upload_progress')
def handle_upload_progress(data):
    socketio.emit('upload_progress_update', data, to=None)

# 定时任务：清理临时文件
def start_scheduler():
    # 先执行一次清理，然后再设置定时任务
    clean_temp_files()
    
    # 设置定时清理任务
    schedule.every(1).hours.do(clean_temp_files)
    
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

# 只有在直接运行此文件时执行以下代码
# 当从main.py导入时，不会执行这些代码
if __name__ == '__main__':
    # 配置日志级别
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    # 启动定时任务线程
    start_scheduler()
    
    # 启动服务器线程
    server_thread = threading.Thread(target=lambda: socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        allow_unsafe_werkzeug=True
    ), daemon=True)
    server_thread.start()

    # 等待服务器启动
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