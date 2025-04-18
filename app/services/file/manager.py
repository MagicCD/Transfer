#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件管理服务模块
提供文件管理相关的功能
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple

from app.services.file.storage import StorageService
from app.services.file.metadata import MetadataService
from app.core.exceptions import FileNotFoundError, FileDeleteError

# 创建日志对象
logger = logging.getLogger(__name__)

class FileManager:
    """文件管理服务"""
    
    @classmethod
    def get_file_info(cls, filename: str) -> Dict[str, Any]:
        """获取文件信息
        
        Args:
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 文件信息
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        # 验证文件是否存在
        file_path = StorageService.get_file_path(filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(filename)
        
        # 获取文件元数据
        return MetadataService.get_file_metadata(file_path, filename)
    
    @classmethod
    def list_files(cls) -> List[Dict[str, Any]]:
        """列出所有文件
        
        Returns:
            List[Dict[str, Any]]: 文件信息列表
        """
        # 获取文件列表
        files = StorageService.list_files()
        
        # 获取每个文件的元数据
        file_info_list = []
        for filename in files:
            try:
                file_path = StorageService.get_file_path(filename)
                file_info = MetadataService.get_file_metadata(file_path, filename)
                file_info_list.append(file_info)
            except Exception as e:
                logger.error(f"获取文件 {filename} 的元数据时出错: {str(e)}")
        
        return file_info_list
    
    @classmethod
    def delete_file(cls, filename: str) -> bool:
        """删除文件
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            FileNotFoundError: 文件不存在
            FileDeleteError: 删除文件失败
        """
        return StorageService.delete_file(filename)
    
    @classmethod
    def delete_all_files(cls) -> Tuple[bool, int]:
        """删除所有文件
        
        Returns:
            Tuple[bool, int]: (是否删除成功, 删除的文件数)
        """
        return StorageService.delete_all_files()
