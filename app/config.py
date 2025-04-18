#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 确定应用程序基础路径 (解决PyInstaller打包后的路径问题)
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe文件
    APPLICATION_PATH = os.path.dirname(sys.executable)
    RUNNING_MODE = "packaged"
else:
    # 如果是直接运行的py脚本
    APPLICATION_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RUNNING_MODE = "script"

logger.info(f"Application Base Path: {APPLICATION_PATH}")
logger.info(f"Running Mode: {RUNNING_MODE}")

# 应用配置
SECRET_KEY = 'your-secret-key'
UPLOAD_FOLDER = os.path.join(APPLICATION_PATH, 'uploads')
MAX_CONTENT_LENGTH = 5 * 1024 * 1024 * 1024  # 5GB
CHUNK_SIZE = 5 * 1024 * 1024  # 5MB
TEMP_CHUNKS_DIR = os.path.join(APPLICATION_PATH, 'uploads', '.temp_chunks')
TEMP_FILES_MAX_AGE = 2  # 临时文件最长保存时间(小时)

# 缓存配置
FILES_CACHE_TTL = 5  # 文件列表缓存有效期（秒）

# 常量定义
KB = 1024
MB = KB * 1024
GB = MB * 1024

# 上传状态常量
UPLOAD_STATUS = {
    'UPLOADING': 'uploading',  # 正在上传
    'PAUSED': 'paused',        # 已暂停
    'COMPLETED': 'completed',  # 已完成
    'FAILED': 'failed',        # 上传失败
    'MERGING': 'merging'       # 正在合并
}

# 文件图标映射
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

# 确保上传目录和临时分块目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_CHUNKS_DIR, exist_ok=True)
