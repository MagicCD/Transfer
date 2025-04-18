#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
上传接口模块
定义文件上传相关的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, BinaryIO


class UploadInterface(ABC):
    """上传接口"""
    
    @abstractmethod
    def upload_file(self, file_obj: BinaryIO, filename: str) -> Dict[str, Any]:
        """上传文件
        
        Args:
            file_obj: 文件对象
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        pass
    
    @abstractmethod
    def validate_upload(self, file_obj: BinaryIO, filename: str) -> bool:
        """验证上传
        
        Args:
            file_obj: 文件对象
            filename: 文件名
            
        Returns:
            bool: 是否验证通过
        """
        pass


class ChunkedUploadInterface(ABC):
    """分块上传接口"""
    
    @abstractmethod
    def upload_chunk(self, file_obj: BinaryIO, filename: str, chunk_number: int, total_chunks: int) -> Dict[str, Any]:
        """上传文件块
        
        Args:
            file_obj: 文件对象
            filename: 文件名
            chunk_number: 块编号
            total_chunks: 总块数
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        pass
    
    @abstractmethod
    def complete_upload(self, filename: str, total_chunks: int) -> Dict[str, Any]:
        """完成上传
        
        Args:
            filename: 文件名
            total_chunks: 总块数
            
        Returns:
            Dict[str, Any]: 完成结果
        """
        pass
    
    @abstractmethod
    def cancel_upload(self, filename: str) -> Dict[str, Any]:
        """取消上传
        
        Args:
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 取消结果
        """
        pass
    
    @abstractmethod
    def get_upload_status(self, filename: str) -> Dict[str, Any]:
        """获取上传状态
        
        Args:
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 上传状态
        """
        pass
