#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import shutil
from datetime import datetime

from app.config import UPLOAD_FOLDER
from app.services.cache.cache_service import invalidate_files_cache, get_files_info

# 创建日志对象
logger = logging.getLogger(__name__)

class FileManager:
    """文件管理核心类，处理文件的基本操作"""
    
    @staticmethod
    def get_file_path(filename):
        """获取文件的完整路径
        
        Args:
            filename (str): 文件名
            
        Returns:
            str: 文件的完整路径
        """
        return os.path.join(UPLOAD_FOLDER, filename)
    
    @staticmethod
    def delete_file(filename):
        """删除单个文件
        
        Args:
            filename (str): 要删除的文件名
            
        Returns:
            bool: 是否成功删除
        """
        try:
            file_path = FileManager.get_file_path(filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"文件已删除: {filename}")
                
                # 使缓存失效
                invalidate_files_cache()
                
                return True
            else:
                logger.warning(f"尝试删除不存在的文件: {filename}")
                return False
        except Exception as e:
            logger.error(f"删除文件时出错: {str(e)}")
            return False
    
    @staticmethod
    def delete_all_files():
        """删除所有文件
        
        Returns:
            tuple: (是否成功, 删除的文件数量)
        """
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
            
            # 使缓存失效
            invalidate_files_cache()
            
            # 记录日志
            logger.info(f"删除了 {deleted_count} 个文件, 删除前: {files_before}, 删除后: {len(get_files_info(force_refresh=True))}")
            
            return True, deleted_count
        except Exception as e:
            logger.error(f"删除所有文件时出错: {str(e)}")
            return False, 0
    
    @staticmethod
    def get_file_info(filename):
        """获取单个文件的信息
        
        Args:
            filename (str): 文件名
            
        Returns:
            dict: 文件信息，如果文件不存在则返回None
        """
        try:
            file_path = FileManager.get_file_path(filename)
            if not os.path.exists(file_path):
                return None
                
            from app.services.file.file_service import format_file_size, get_file_icon
            
            size = os.path.getsize(file_path)
            modified_time = os.path.getmtime(file_path)
            modified_time_str = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                'name': filename,
                'size': size,
                'size_formatted': format_file_size(size),
                'icon': get_file_icon(filename),
                'modified_time': modified_time_str
            }
        except Exception as e:
            logger.error(f"获取文件信息时出错: {str(e)}")
            return None
