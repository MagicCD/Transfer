#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件元数据服务
负责文件元数据的管理，如获取文件信息、图标等
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from app.core.config import UPLOAD_FOLDER, ICON_MAPPING
from app.services.file.storage import StorageService
from app.utils.formatter import format_file_size
from app.core.exceptions import FileNotFoundError

# 创建日志对象
logger = logging.getLogger(__name__)

class MetadataService:
    """文件元数据服务类，处理文件信息相关操作"""

    @staticmethod
    def get_file_icon(filename: str) -> str:
        """根据文件扩展名获取对应的图标

        Args:
            filename: 文件名

        Returns:
            图标类名
        """
        # 获取文件扩展名（小写）
        _, ext = os.path.splitext(filename.lower())

        # 返回对应的图标，如果没有匹配项则返回默认图标
        return ICON_MAPPING.get(ext, 'fa-file')

    @staticmethod
    def get_file_info(filename: str) -> Dict[str, Union[str, int]]:
        """获取文件信息

        Args:
            filename: 文件名

        Returns:
            文件信息字典

        Raises:
            FileNotFoundError: 当文件不存在时
        """
        file_path = StorageService.get_file_path(filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(filename)

        size = os.path.getsize(file_path)
        modified_time = os.path.getmtime(file_path)
        modified_time_str = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')

        return {
            'name': filename,
            'size': size,
            'size_formatted': format_file_size(size),
            'icon': MetadataService.get_file_icon(filename),
            'modified_time': modified_time_str
        }

    @staticmethod
    def get_files_info(force_refresh: bool = False) -> List[Dict[str, Union[str, int]]]:
        """获取所有文件的信息

        Args:
            force_refresh: 是否强制刷新缓存

        Returns:
            文件信息列表
        """
        # 获取文件列表
        files_list = StorageService.get_files_list()

        # 获取每个文件的详细信息
        files_info = []
        for filename in files_list:
            try:
                file_info = MetadataService.get_file_info(filename)
                files_info.append(file_info)
            except Exception as e:
                logger.error(f"获取文件信息时出错: {filename}, {str(e)}")

        # 按修改时间排序，最新的文件在前面
        files_info.sort(key=lambda x: x.get('modified_time', ''), reverse=True)

        return files_info
