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
import hashlib
import mmap
import asyncio
import aiofiles
# from werkzeug.utils import secure_filename  # 未使用，注释掉
import gc  # 垃圾回收模块

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

# 确定应用程序基础路径 (解决PyInstaller打包后的路径问题)
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe文件
    application_path = os.path.dirname(sys.executable)
    running_mode = "packaged"
else:
    # 如果是直接运行的py脚本
    application_path = os.path.dirname(os.path.abspath(__file__))
    running_mode = "script"

logger.info(f"Application Base Path: {application_path}")
logger.info(f"Running Mode: {running_mode}")

from flask import Flask, render_template, request, send_from_directory, jsonify, abort
from flask_socketio import SocketIO

# 创建应用并使用resource_path处理静态文件和模板路径
# 注意：resource_path 用于访问打包到程序内部的资源 (templates, static)
templates_dir = resource_path('templates')
static_dir = resource_path('static') if os.path.exists(resource_path('static')) else None

app = Flask(__name__,
            template_folder=templates_dir,
            static_url_path='/static',
            static_folder=static_dir)

app.config['SECRET_KEY'] = 'your-secret-key'
# 修改 UPLOAD_FOLDER 和 TEMP_CHUNKS_DIR 使用绝对路径
app.config['UPLOAD_FOLDER'] = os.path.join(application_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 5GB
app.config['CHUNK_SIZE'] = 5 * 1024 * 1024  # 5MB
# TEMP_CHUNKS_DIR 也应基于 application_path
app.config['TEMP_CHUNKS_DIR'] = os.path.join(application_path, 'uploads', '.temp_chunks')
app.config['TEMP_FILES_MAX_AGE'] = 2  # 临时文件最长保存时间(小时)

# 初始化 Socket.IO - 指定async_mode为threading，避免使用eventlet或gevent
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*", logger=False, engineio_logger=False)

# 确保上传目录和临时分块目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_CHUNKS_DIR'], exist_ok=True)

# 自定义错误处理
@app.errorhandler(413)
def request_entity_too_large(_):
    # 使用下划线作为参数名表示我们不使用这个参数
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

# 文件图标缓存字典
file_icon_cache = {}

# 预定义图标映射
ICON_MAPPING = {
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

# 获取文件图标 - 优化版本
def get_file_icon(filename):
    # 检查缓存中是否已有此文件的图标
    if filename in file_icon_cache:
        return file_icon_cache[filename]

    filename_lower = filename.lower()

    # 处理复合扩展名
    if filename_lower.endswith('.tar.gz') or filename_lower.endswith('.tar.bz2'):
        icon = 'fa-file-archive'
    else:
        # 处理单一扩展名
        extension = os.path.splitext(filename_lower)[1]
        # 直接从映射中获取图标
        icon = ICON_MAPPING.get(extension, 'fa-file')

    # 将结果存入缓存
    file_icon_cache[filename] = icon
    return icon

# 文件大小格式化缓存
file_size_cache = {}

# 定义单位常量
KB = 1024
MB = KB * 1024
GB = MB * 1024

# 格式化文件大小
def format_file_size(size_bytes):
    # 检查缓存中是否已有此大小的格式化结果
    if size_bytes in file_size_cache:
        return file_size_cache[size_bytes]

    # 计算格式化结果
    if size_bytes < KB:
        result = f"{size_bytes} B"
    elif size_bytes < MB:
        result = f"{size_bytes / KB:.2f} KB"
    elif size_bytes < GB:
        result = f"{size_bytes / MB:.2f} MB"
    else:
        result = f"{size_bytes / GB:.2f} GB"

    # 将结果存入缓存
    file_size_cache[size_bytes] = result
    return result

# 删除部分写入的文件
def remove_partial_file(file_path):
    """删除部分写入的文件，避免损坏文件残留"""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"已删除部分写入的文件: {file_path}")
            return True
        except Exception as del_error:
            logger.error(f"无法删除部分写入的文件: {str(del_error)}")
            return False
    return False

# 清理指定文件的损坏块
def clean_corrupted_chunks(filename, corrupted_chunk_indices=None):
    """清理指定文件的损坏块

    Args:
        filename: 文件名
        corrupted_chunk_indices: 损坏块的索引列表，如果为None，则检查所有块

    Returns:
        tuple: (清理的块数, 损坏块列表)
    """
    try:
        file_temp_dir = os.path.join(app.config['TEMP_CHUNKS_DIR'], filename)
        if not os.path.exists(file_temp_dir):
            logger.warning(f"文件的临时目录不存在: {filename}")
            return 0, []

        cleaned_count = 0
        corrupted_chunks = []

        # 如果指定了损坏块索引，只清理这些块
        if corrupted_chunk_indices:
            for i in corrupted_chunk_indices:
                # 删除所有匹配的块文件
                for chunk_file in os.listdir(file_temp_dir):
                    if chunk_file.startswith(f"chunk_{i}_"):
                        chunk_path = os.path.join(file_temp_dir, chunk_file)
                        try:
                            os.remove(chunk_path)
                            cleaned_count += 1
                            if i not in corrupted_chunks:
                                corrupted_chunks.append(i)
                            logger.info(f"删除损坏块: {chunk_path}")
                        except Exception as e:
                            logger.error(f"删除损坏块时出错: {chunk_path}, {str(e)}")
        else:
            # 检查所有块，分析块的完整性
            # 首先收集所有块索引
            chunk_indices = set()
            for chunk_file in os.listdir(file_temp_dir):
                if chunk_file.startswith("chunk_") and "_" in chunk_file:
                    try:
                        chunk_index = int(chunk_file.split("_")[1])
                        chunk_indices.add(chunk_index)
                    except (ValueError, IndexError):
                        pass

            # 检查每个块索引的文件是否完整
            for chunk_index in chunk_indices:
                # 获取该块索引的所有文件
                chunk_files = [f for f in os.listdir(file_temp_dir) if f.startswith(f"chunk_{chunk_index}_")]

                # 如果有多个文件匹配同一个块索引，只保留最新的一个
                if len(chunk_files) > 1:
                    # 按修改时间排序
                    chunk_files.sort(key=lambda f: os.path.getmtime(os.path.join(file_temp_dir, f)), reverse=True)

                    # 删除旧文件
                    for old_file in chunk_files[1:]:
                        old_path = os.path.join(file_temp_dir, old_file)
                        try:
                            os.remove(old_path)
                            cleaned_count += 1
                            logger.info(f"删除重复块文件: {old_path}")
                        except Exception as e:
                            logger.error(f"删除重复块文件时出错: {old_path}, {str(e)}")

        return cleaned_count, corrupted_chunks
    except Exception as e:
        logger.error(f"清理损坏块时出错: {str(e)}")
        return 0, []

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

# 文件信息缓存
files_info_cache = {}
files_info_cache_time = 0
FILES_CACHE_TTL = 5  # 缓存有效期（秒）
files_info_cache_hits = 0  # 缓存命中次数
files_info_cache_misses = 0  # 缓存未命中次数
files_info_cache_invalidations = 0  # 缓存手动失效次数

# 使缓存失效
def invalidate_files_cache():
    """手动使文件列表缓存失效"""
    global files_info_cache, files_info_cache_time, files_info_cache_invalidations
    files_info_cache = {}
    files_info_cache_time = 0
    files_info_cache_invalidations += 1
    logger.debug(f"文件列表缓存已手动失效, 总失效次数: {files_info_cache_invalidations}")

# 获取所有文件信息
def get_files_info(force_refresh=False):
    global files_info_cache, files_info_cache_time, files_info_cache_hits, files_info_cache_misses

    # 检查缓存是否有效
    current_time = time.time()
    cache_age = current_time - files_info_cache_time

    # 如果缓存有效且不需要强制刷新，直接返回缓存的数据
    if not force_refresh and files_info_cache and cache_age < FILES_CACHE_TTL:
        files_info_cache_hits += 1
        logger.debug(f"文件列表缓存命中，年龄: {cache_age:.2f}秒, 总命中次数: {files_info_cache_hits}")
        return files_info_cache

    # 缓存未命中或需要强制刷新，重新获取文件列表
    files_info_cache_misses += 1
    if force_refresh:
        logger.debug(f"强制刷新文件列表缓存, 总未命中次数: {files_info_cache_misses}")
    else:
        logger.debug(f"文件列表缓存过期 (年龄: {cache_age:.2f}秒), 总未命中次数: {files_info_cache_misses}")

    files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                modified_time = os.path.getmtime(file_path)
                modified_time_str = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')

                files.append({
                    'name': filename,
                    'size': size,
                    'size_formatted': format_file_size(size),
                    'icon': get_file_icon(filename),
                    'modified_time': modified_time_str
                })

    # 更新缓存
    files_info_cache = sorted(files, key=lambda x: x['name'])
    files_info_cache_time = current_time
    logger.debug(f"文件列表缓存已更新, 包含 {len(files)} 个文件")

    return files_info_cache

# 路由处理

@app.route('/')
def index():
    return render_template('index.html',
                           server_ip=get_local_ip(),
                           server_port=5000,
                           files=get_files_info(force_refresh=False))

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否有文件部分
    if 'file' not in request.files:
        return jsonify(success=False, error='No file part')

    file = request.files['file']

    # 如果用户没有选择文件
    if file.filename == '':
        return jsonify(success=False, error='No selected file')

    # 获取文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # 重置文件指针到开始位置

    # 检查文件大小，如果大于50MB，返回需要使用分块上传的提示
    if file_size >= 50 * 1024 * 1024:  # 50MB
        logger.info(f"文件 {file.filename} 大小为 {file_size} 字节，需要使用分块上传")
        return jsonify(
            success=False,
            error='Large file detected',
            use_chunked_upload=True,
            file_size=file_size,
            message='此文件大小超过50MB，需要使用分块上传'
        )

    # 保存文件（小于50MB的文件）
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

        # 手动使缓存失效
        invalidate_files_cache()

        # 通知所有客户端文件已更新
        socketio.emit('files_updated', {'files': get_files_info(force_refresh=True)})

        return jsonify(success=True, filename=filename)
    except Exception as e:
        logger.error(f"上传文件时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

async def merge_chunks_async(file_temp_dir, final_path, total_chunks):
    """使用流式处理合并文件块，避免高内存消耗"""
    start_time = time.time()
    logger.info(f"开始合并文件块，总块数: {total_chunks}，目标文件: {final_path}")

    # 检查所有块是否存在
    missing_chunks = []
    chunk_files = {}  # 存储每个块索引对应的文件路径

    # 首先收集所有块文件
    for filename in os.listdir(file_temp_dir):
        if filename.startswith("chunk_") and "_" in filename:
            try:
                # 从文件名中提取块索引
                chunk_index = int(filename.split('_')[1])
                chunk_files[chunk_index] = os.path.join(file_temp_dir, filename)
            except (ValueError, IndexError):
                logger.warning(f"无法解析块文件名: {filename}")

    # 检查是否有缺失的块
    for i in range(total_chunks):
        if i not in chunk_files:
            missing_chunks.append(i)

    if missing_chunks:
        logger.error(f"合并失败: 缺少以下块: {missing_chunks}")
        return False

    try:
        # 创建最终文件
        async with aiofiles.open(final_path, 'wb') as outfile:
            total_bytes_written = 0

            # 按顺序处理每个块
            for i in range(total_chunks):
                chunk_file_path = chunk_files[i]

                # 直接流式读取并写入块数据
                async with aiofiles.open(chunk_file_path, 'rb') as chunk_file:
                    # 使用缓冲区读取并写入，避免将整个块加载到内存
                    buffer_size = 1024 * 1024  # 1MB缓冲区
                    bytes_written = 0

                    while True:
                        buffer = await chunk_file.read(buffer_size)
                        if not buffer:
                            break

                        await outfile.write(buffer)
                        bytes_written += len(buffer)
                        total_bytes_written += len(buffer)

                # 每处理10个块或处理完最后一个块时报告进度
                if (i + 1) % 10 == 0 or i == total_chunks - 1:
                    progress = ((i + 1) / total_chunks) * 100
                    logger.info(f"合并进度: {progress:.1f}%, 已写入: {format_file_size(total_bytes_written)}")

                # 定期强制垃圾回收
                if (i + 1) % 50 == 0:
                    gc.collect()

        # 验证最终文件大小
        final_size = os.path.getsize(final_path)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"文件合并完成，大小: {format_file_size(final_size)}，耗时: {duration:.2f}秒")

        return True
    except Exception as e:
        logger.error(f"异步合并文件块时出错: {str(e)}")
        # 删除部分写入的文件
        remove_partial_file(final_path)
        return False

async def process_chunk(chunk_file_path, chunk_index, chunk_data):
    """异步处理单个分块 - 保留用于兼容性"""
    try:
        # 获取文件大小
        file_size = os.path.getsize(chunk_file_path)

        # 对于小文件，直接读取而不使用内存映射
        if file_size < 1024 * 1024:  # 小于1MB的文件
            async with aiofiles.open(chunk_file_path, 'rb') as infile:
                chunk_content = await infile.read()
                # 计算块的MD5校验和
                chunk_hash = hashlib.md5(chunk_content).hexdigest()

                # 检查是否已经上传过这个块
                chunk_hash_file = f"{chunk_file_path}.hash"
                if os.path.exists(chunk_hash_file):
                    with open(chunk_hash_file, 'r') as hash_file:
                        existing_hash = hash_file.read().strip()
                        if existing_hash == chunk_hash:
                            # 块已经上传过，使用空数据替代
                            chunk_data[chunk_index] = b''
                            return

                # 保存块的校验和
                async with aiofiles.open(chunk_hash_file, 'w') as hash_file:
                    await hash_file.write(chunk_hash)

                # 存储数据
                chunk_data[chunk_index] = chunk_content
        else:
            # 对于大文件，使用内存映射
            with open(chunk_file_path, 'rb') as infile:
                with mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # 计算块的MD5校验和
                    chunk_hash = hashlib.md5(mm).hexdigest()

                    # 检查是否已经上传过这个块
                    chunk_hash_file = f"{chunk_file_path}.hash"
                    if os.path.exists(chunk_hash_file):
                        with open(chunk_hash_file, 'r') as hash_file:
                            existing_hash = hash_file.read().strip()
                            if existing_hash == chunk_hash:
                                # 块已经上传过，使用空数据替代
                                chunk_data[chunk_index] = b''
                                return

                    # 保存块的校验和
                    with open(chunk_hash_file, 'w') as hash_file:
                        hash_file.write(chunk_hash)

                    # 读取数据并存储在字典中
                    chunk_data[chunk_index] = mm.read()
    except Exception as e:
        logger.error(f"处理分块 {chunk_index} 时出错: {str(e)}")
        # 放入空数据以保持索引完整性
        chunk_data[chunk_index] = b''

async def process_chunk_streaming(chunk_file_path, chunk_index, outfile):
    """流式处理单个分块并直接写入输出文件，避免高内存消耗"""
    try:
        # 获取文件大小
        file_size = os.path.getsize(chunk_file_path)
        if file_size == 0:
            logger.warning(f"分块 {chunk_index} 大小为0，跳过")
            return 0

        # 检查是否已经上传过这个块
        chunk_hash_file = f"{chunk_file_path}.hash"
        chunk_hash = None

        # 对于小文件，直接读取并处理
        if file_size < 1024 * 1024:  # 小于1MB的文件
            async with aiofiles.open(chunk_file_path, 'rb') as infile:
                chunk_content = await infile.read()
                # 计算块的MD5校验和
                chunk_hash = hashlib.md5(chunk_content).hexdigest()

                # 检查是否已经上传过这个块
                if os.path.exists(chunk_hash_file):
                    with open(chunk_hash_file, 'r') as hash_file:
                        existing_hash = hash_file.read().strip()
                        if existing_hash == chunk_hash:
                            # 块已经上传过，跳过写入
                            return 0

                # 直接写入数据到输出文件
                await outfile.write(chunk_content)

                # 保存块的校验和
                async with aiofiles.open(chunk_hash_file, 'w') as hash_file:
                    await hash_file.write(chunk_hash)

                return len(chunk_content)
        else:
            # 对于大文件，使用内存映射并分块读取写入
            with open(chunk_file_path, 'rb') as infile:
                # 首先计算MD5校验和
                with mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    chunk_hash = hashlib.md5(mm).hexdigest()

                    # 检查是否已经上传过这个块
                    if os.path.exists(chunk_hash_file):
                        with open(chunk_hash_file, 'r') as hash_file:
                            existing_hash = hash_file.read().strip()
                            if existing_hash == chunk_hash:
                                # 块已经上传过，跳过写入
                                return 0

                    # 分块读取并写入，避免一次性加载整个文件到内存
                    # 重置内存映射位置
                    mm.seek(0)

                    # 使用较小的缓冲区分块读取和写入
                    buffer_size = 1024 * 1024  # 1MB缓冲区
                    bytes_written = 0

                    while True:
                        buffer = mm.read(buffer_size)
                        if not buffer:
                            break

                        await outfile.write(buffer)
                        bytes_written += len(buffer)

                    # 保存块的校验和
                    with open(chunk_hash_file, 'w') as hash_file:
                        hash_file.write(chunk_hash)

                    return bytes_written
    except Exception as e:
        logger.error(f"流式处理分块 {chunk_index} 时出错: {str(e)}")
        return 0

# 计算文件块的MD5哈希值
def calculate_chunk_hash(chunk_data):
    """计算数据块的MD5哈希值"""
    return hashlib.md5(chunk_data).hexdigest()

# 生成基于哈希的块文件名
def get_chunk_filename(chunk_number, chunk_hash):
    """生成包含哈希值的块文件名，便于验证和重复数据检测"""
    return f"chunk_{chunk_number}_{chunk_hash}"

@app.route('/upload/chunk', methods=['POST'])
def upload_chunk():
    # 获取参数
    chunk_number = int(request.form.get('chunk_number', 0))
    total_chunks = int(request.form.get('total_chunks', 0))
    filename = request.form.get('filename', '')

    # 检查参数
    if not filename or 'file' not in request.files:
        return jsonify(success=False, error='Invalid request parameters')

    # 确保文件名安全
    filename = os.path.basename(filename)
    chunk = request.files['file']
    file_temp_dir = None

    try:
        # 初始化上传状态（如果不存在）
        if filename not in upload_states:
            upload_states[filename] = {
                'status': UPLOAD_STATUS['UPLOADING'],
                'last_chunk': 0,
                'total_chunks': total_chunks,
                'timestamp': datetime.now(),
                'uploaded_chunks': set(),
                'failed_chunks': set(),
                'error': None
            }

        # 获取文件状态
        file_state = upload_states[filename]

        # 检查是否暂停上传
        if file_state['status'] == UPLOAD_STATUS['PAUSED']:
            logger.info(f"文件上传已暂停: {filename}, 当前块: {chunk_number}")
            return jsonify(success=False, error='Upload paused', paused=True)

        # 为此文件创建一个唯一目录
        file_temp_dir = os.path.join(app.config['TEMP_CHUNKS_DIR'], filename)
        os.makedirs(file_temp_dir, exist_ok=True)

        # 读取块数据并计算哈希值
        chunk_data = chunk.read()
        chunk_hash = calculate_chunk_hash(chunk_data)

        # 生成基于哈希的块文件名
        chunk_filename = get_chunk_filename(chunk_number, chunk_hash)
        chunk_path = os.path.join(file_temp_dir, chunk_filename)

        # 检查该块是否已经上传
        chunk_exists = False
        for existing_file in os.listdir(file_temp_dir):
            if existing_file.startswith(f"chunk_{chunk_number}_"):
                # 已存在相同块索引的文件
                existing_path = os.path.join(file_temp_dir, existing_file)
                existing_hash = existing_file.split('_')[-1] if len(existing_file.split('_')) > 2 else None

                if existing_hash == chunk_hash:
                    # 相同的哈希值，块已存在
                    chunk_exists = True
                    chunk_path = existing_path
                    logger.info(f"块 {chunk_number} 已存在，哈希值匹配: {chunk_hash}")
                    break
                else:
                    # 不同的哈希值，删除旧块
                    try:
                        os.remove(existing_path)
                        logger.info(f"删除旧块: {existing_file}, 将替换为新块: {chunk_filename}")
                    except Exception as del_err:
                        logger.error(f"删除旧块时出错: {str(del_err)}")

        # 如果块不存在，则保存
        if not chunk_exists:
            # 将块数据写入文件
            with open(chunk_path, 'wb') as f:
                f.write(chunk_data)
            logger.info(f"保存块 {chunk_number}/{total_chunks-1}, 哈希值: {chunk_hash}")

        # 更新上传状态
        file_state['last_chunk'] = max(file_state.get('last_chunk', 0), chunk_number + 1)
        file_state['timestamp'] = datetime.now()
        file_state['uploaded_chunks'].add(chunk_number)

        # 如果该块之前在失败列表中，则移除
        if chunk_number in file_state['failed_chunks']:
            file_state['failed_chunks'].remove(chunk_number)

        # 如果这是最后一个块或所有块都已上传，合并所有块
        all_chunks_uploaded = len(file_state['uploaded_chunks']) == total_chunks
        is_last_chunk = chunk_number == total_chunks - 1

        if is_last_chunk or all_chunks_uploaded:
            # 更新状态为合并中
            file_state['status'] = UPLOAD_STATUS['MERGING']

            # 使用异步IO合并块
            final_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # 使用 asyncio.run() 替代手动管理事件循环
            try:
                success = asyncio.run(merge_chunks_async(file_temp_dir, final_path, total_chunks))
            except RuntimeError as e:
                # 处理已有事件循环的情况
                if "There is no current event loop in thread" in str(e):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(merge_chunks_async(file_temp_dir, final_path, total_chunks))
                    loop.close()
                else:
                    # 删除部分写入的文件
                    remove_partial_file(final_path)
                    raise

            if not success:
                # 合并失败，更新状态并记录错误
                file_state['status'] = UPLOAD_STATUS['FAILED']
                file_state['error'] = 'Failed to merge chunks'

                # 检查是否有缺失的块
                missing_chunks = []
                for i in range(total_chunks):
                    found = False
                    for existing_file in os.listdir(file_temp_dir):
                        if existing_file.startswith(f"chunk_{i}_"):
                            found = True
                            break
                    if not found:
                        missing_chunks.append(i)
                        file_state['failed_chunks'].add(i)

                if missing_chunks:
                    logger.warning(f"发现缺失的块: {missing_chunks}")

                logger.error(f"合并文件块失败: {filename}")
                return jsonify(
                    success=False,
                    error='Failed to merge chunks',
                    merge_failed=True,
                    missing_chunks=missing_chunks
                )

            # 合并成功，清理临时文件
            try:
                shutil.rmtree(file_temp_dir)
                file_temp_dir = None  # 标记为已清理
            except Exception as e:
                logger.error(f"清理临时分块目录出错: {str(e)}")

            # 更新状态为完成并从上传状态中移除
            file_state['status'] = UPLOAD_STATUS['COMPLETED']
            # 延迟删除状态，给前端时间查询完成状态
            # 定时清理任务会清理过期的状态

            # 手动使缓存失效
            invalidate_files_cache()

            # 通知所有客户端文件已更新
            socketio.emit('files_updated', {'files': get_files_info(force_refresh=True)})

            return jsonify(success=True, filename=filename, status='completed')

        # 返回块上传成功状态
        return jsonify(success=True, filename=filename, status='chunk_uploaded')

    except Exception as e:
        logger.error(f"处理分块上传时出错: {str(e)}")

        # 删除部分写入的文件
        final_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        remove_partial_file(final_path)

        # 更新上传状态，标记错误
        if filename in upload_states:
            upload_states[filename]['status'] = UPLOAD_STATUS['FAILED']
            upload_states[filename]['error'] = str(e)
            upload_states[filename]['timestamp'] = datetime.now()
            if 'failed_chunks' in upload_states[filename] and chunk_number is not None:
                upload_states[filename]['failed_chunks'].add(chunk_number)

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
    try:
        # 记录删除前的文件数量
        files_before = len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))])

        # 删除所有文件
        deleted_count = 0
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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

@app.route('/cancel_upload/<filename>', methods=['POST'])
def cancel_upload(filename):
    """取消文件上传并清理临时文件"""
    try:
        # 清理临时目录下该文件的分块
        file_temp_dir = os.path.join(app.config['TEMP_CHUNKS_DIR'], filename)
        cleaned_count = 0

        if os.path.exists(file_temp_dir):
            try:
                # 删除整个临时目录
                shutil.rmtree(file_temp_dir)
                logger.info(f"已删除临时目录: {file_temp_dir}")
                cleaned_count = 1  # 标记已清理
            except Exception as del_err:
                logger.error(f"删除临时目录时出错: {str(del_err)}")

        # 更新上传状态
        if filename in upload_states:
            # 如果需要保留状态信息以便前端查询，可以将状态设置为已取消
            # 而不是直接删除状态
            upload_states[filename] = {
                'status': UPLOAD_STATUS['COMPLETED'],  # 标记为完成状态，便于前端处理
                'timestamp': datetime.now(),
                'error': 'Upload cancelled by user',
                'uploaded_chunks': set(),
                'failed_chunks': set()
            }

            # 延迟删除状态，定时清理任务会清理过期的状态
            logger.info(f"已将上传状态标记为已取消: {filename}")

        # 通知所有客户端上传状态已更新
        socketio.emit('upload_state_updated', {
            'filename': filename,
            'status': 'cancelled',
            'paused': False
        })

        return jsonify(
            success=True,
            message=f'已取消上传并清理临时文件: {filename}',
            cleaned=cleaned_count > 0
        )
    except Exception as e:
        logger.error(f"取消上传时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

# 上传状态管理
# 定义上传状态常量
UPLOAD_STATUS = {
    'UPLOADING': 'uploading',  # 正在上传
    'PAUSED': 'paused',        # 已暂停
    'COMPLETED': 'completed',  # 已完成
    'FAILED': 'failed',        # 上传失败
    'MERGING': 'merging'       # 正在合并
}

# 使用字典存储上传状态信息
# {filename: {
#     'status': UPLOAD_STATUS['UPLOADING'],  # 当前状态
#     'last_chunk': 12,                      # 最后上传的块索引
#     'total_chunks': 100,                   # 总块数
#     'timestamp': datetime.now(),           # 最后更新时间
#     'error': None,                         # 错误信息
#     'uploaded_chunks': set(),              # 已上传的块集合
#     'failed_chunks': set()                 # 上传失败的块集合
# }}
upload_states = {}

@app.route('/pause_upload/<filename>', methods=['POST'])
def pause_upload(filename):
    """暂停特定文件上传的API"""
    try:
        # 从请求获取当前块索引
        data = request.get_json() or {}
        chunk_index = data.get('chunk_index', 0)

        # 获取文件的上传状态
        if filename not in upload_states:
            # 创建新的状态记录
            upload_states[filename] = {
                'status': UPLOAD_STATUS['PAUSED'],
                'last_chunk': chunk_index,
                'timestamp': datetime.now(),
                'uploaded_chunks': set(),
                'failed_chunks': set(),
                'error': None
            }
        else:
            # 更新现有状态
            file_state = upload_states[filename]

            # 更新状态
            file_state['status'] = UPLOAD_STATUS['PAUSED']
            file_state['last_chunk'] = max(file_state.get('last_chunk', 0), chunk_index)
            file_state['timestamp'] = datetime.now()

        # 通知所有客户端上传状态已更新
        socketio.emit('upload_state_updated', {
            'filename': filename,
            'status': UPLOAD_STATUS['PAUSED'],
            'chunk_index': chunk_index,
            'paused': True
        })

        logger.info(f"暂停上传文件: {filename}, 当前块: {chunk_index}")
        return jsonify(success=True, message=f'已暂停上传: {filename}')
    except Exception as e:
        logger.error(f"暂停上传时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

@app.route('/resume_upload/<filename>', methods=['POST'])
def resume_upload(filename):
    """恢复特定文件上传的API"""
    try:
        # 获取文件的状态
        if filename not in upload_states:
            return jsonify(success=False, error='File not found in upload states')

        file_state = upload_states[filename]
        last_chunk = file_state.get('last_chunk', 0)
        current_status = file_state.get('status')

        # 检查是否有临时目录
        file_temp_dir = os.path.join(app.config['TEMP_CHUNKS_DIR'], filename)
        has_temp_dir = os.path.exists(file_temp_dir)

        # 如果当前状态是失败，检查并清理失败的块
        cleaned_count = 0
        if current_status == UPLOAD_STATUS['FAILED'] and has_temp_dir:
            failed_chunks = list(file_state.get('failed_chunks', set()))
            if failed_chunks:
                # 删除失败的块文件，以便重新上传
                for chunk_index in failed_chunks:
                    # 删除对应块索引的所有文件
                    for filename_in_dir in os.listdir(file_temp_dir):
                        if filename_in_dir.startswith(f"chunk_{chunk_index}_"):
                            try:
                                os.remove(os.path.join(file_temp_dir, filename_in_dir))
                                cleaned_count += 1
                                logger.info(f"删除失败的块文件: {filename_in_dir}")
                            except Exception as del_err:
                                logger.error(f"删除失败块时出错: {str(del_err)}")

                # 清空失败块集合
                file_state['failed_chunks'] = set()
                logger.info(f"已清理 {cleaned_count} 个失败块，准备重新上传")

        # 更新状态为上传中
        file_state['status'] = UPLOAD_STATUS['UPLOADING']
        file_state['timestamp'] = datetime.now()
        file_state['error'] = None  # 清除错误信息

        # 通知所有客户端上传状态已更新
        socketio.emit('upload_state_updated', {
            'filename': filename,
            'status': UPLOAD_STATUS['UPLOADING'],
            'chunk_index': last_chunk,
            'paused': False,
            'has_temp_dir': has_temp_dir
        })

        logger.info(f"恢复上传文件: {filename}, 从块 {last_chunk} 开始, 是否有临时目录: {has_temp_dir}")
        return jsonify(
            success=True,
            message=f'已恢复上传: {filename}',
            last_chunk=last_chunk,
            has_temp_dir=has_temp_dir,
            cleaned_chunks=cleaned_count
        )
    except Exception as e:
        logger.error(f"恢复上传时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

@app.route('/upload_state/<filename>', methods=['GET'])
def get_upload_state(filename):
    """获取文件上传状态的API"""
    try:
        # 获取文件的状态
        file_state = upload_states.get(filename, {})
        if not file_state:
            return jsonify(
                success=True,
                status=UPLOAD_STATUS['COMPLETED'],  # 默认完成状态
                paused=False,
                last_chunk=0,
                total_chunks=0,
                upload_in_progress=False,
                error=None
            )

        # 检查是否有临时目录，判断上传是否正在进行
        file_temp_dir = os.path.join(app.config['TEMP_CHUNKS_DIR'], filename)
        upload_in_progress = os.path.exists(file_temp_dir)

        # 获取当前状态
        current_status = file_state.get('status', UPLOAD_STATUS['COMPLETED'])

        # 如果没有临时目录但状态不是完成，可能是已完成或已取消
        if not upload_in_progress and current_status not in [UPLOAD_STATUS['COMPLETED'], UPLOAD_STATUS['PAUSED']]:
            current_status = UPLOAD_STATUS['COMPLETED']

        # 计算上传进度
        total_chunks = file_state.get('total_chunks', 0)
        uploaded_chunks = len(file_state.get('uploaded_chunks', set()))
        progress = 0
        if total_chunks > 0:
            progress = int((uploaded_chunks / total_chunks) * 100)

        # 返回更完整的状态信息
        return jsonify(
            success=True,
            status=current_status,
            paused=(current_status == UPLOAD_STATUS['PAUSED']),
            last_chunk=file_state.get('last_chunk', 0),
            total_chunks=total_chunks,
            uploaded_chunks=uploaded_chunks,
            progress=progress,
            upload_in_progress=upload_in_progress,
            error=file_state.get('error'),
            failed_chunks=list(file_state.get('failed_chunks', set())),
            timestamp=file_state.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S') if 'timestamp' in file_state else None
        )
    except Exception as e:
        logger.error(f"获取上传状态时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

# 获取文件列表的API端点
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
            'cache_time': files_info_cache_time,
            'current_time': time.time(),
            'cache_ttl': FILES_CACHE_TTL
        })
    except Exception as e:
        logger.error(f"获取文件列表时出错: {str(e)}")
        return jsonify(success=False, error=str(e))

# Socket.IO 事件处理
@socketio.on('connect')
def handle_connect():
    # 连接时发送最新的文件列表，强制刷新缓存
    socketio.emit('files_updated', {'files': get_files_info(force_refresh=True)})

@socketio.on('upload_progress')
def handle_upload_progress(data):
    socketio.emit('upload_progress_update', data, to=None)

# 定时任务：清理临时文件和缓存
def start_scheduler():
    # 先执行一次清理，然后再设置定时任务
    clean_temp_files()

    # 设置定时清理任务
    schedule.every(1).hours.do(clean_temp_files)

    # 设置定时清理缓存任务
    def clean_caches():
        global file_icon_cache, file_size_cache, files_info_cache, files_info_cache_time
        logger.info("清理内存缓存...")

        # 清理所有缓存
        cache_sizes = {
            '文件图标缓存': len(file_icon_cache),
            '文件大小缓存': len(file_size_cache)
        }

        # 重置所有缓存
        file_icon_cache.clear()
        file_size_cache.clear()
        files_info_cache = {}
        files_info_cache_time = 0

        # 记录清理的缓存大小
        for cache_name, size in cache_sizes.items():
            logger.info(f"已清理{cache_name}: {size} 项")

        # 强制垃圾回收
        gc.collect()

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

    # 创建webview窗口
    server_url = f"http://{get_local_ip()}:5000"
    window = webview.create_window('内网文件传输工具', server_url, width=900, height=700)
    webview.start(lambda: exit_event.set())