#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
常量配置模块
定义应用程序中使用的所有常量
"""

# 文件大小单位常量
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
