#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件存储接口模块
定义文件存储相关的抽象接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, BinaryIO


class FileStorageInterface(ABC):
    """文件存储接口"""
    
    @abstractmethod
    def save_file(self, file_obj: BinaryIO, filename: str) -> str:
        """保存文件
        
        Args:
            file_obj: 文件对象
            filename: 文件名
            
        Returns:
            str: 保存后的文件路径
        """
        pass
    
    @abstractmethod
    def delete_file(self, filename: str) -> bool:
        """删除文件
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    def get_file_path(self, filename: str) -> str:
        """获取文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            str: 文件路径
        """
        pass
    
    @abstractmethod
    def list_files(self) -> List[Dict[str, Any]]:
        """列出所有文件
        
        Returns:
            List[Dict[str, Any]]: 文件信息列表
        """
        pass
    
    @abstractmethod
    def file_exists(self, filename: str) -> bool:
        """检查文件是否存在
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 文件是否存在
        """
        pass


class ChunkStorageInterface(ABC):
    """分块存储接口"""
    
    @abstractmethod
    def save_chunk(self, file_obj: BinaryIO, filename: str, chunk_number: int) -> str:
        """保存文件块
        
        Args:
            file_obj: 文件对象
            filename: 文件名
            chunk_number: 块编号
            
        Returns:
            str: 保存后的块文件路径
        """
        pass
    
    @abstractmethod
    def merge_chunks(self, filename: str, total_chunks: int) -> str:
        """合并文件块
        
        Args:
            filename: 文件名
            total_chunks: 总块数
            
        Returns:
            str: 合并后的文件路径
        """
        pass
    
    @abstractmethod
    def delete_chunks(self, filename: str) -> bool:
        """删除文件的所有块
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    def get_chunk_path(self, filename: str, chunk_number: int) -> str:
        """获取块文件路径
        
        Args:
            filename: 文件名
            chunk_number: 块编号
            
        Returns:
            str: 块文件路径
        """
        pass
    
    @abstractmethod
    def list_chunks(self, filename: str) -> List[int]:
        """列出文件的所有块
        
        Args:
            filename: 文件名
            
        Returns:
            List[int]: 块编号列表
        """
        pass
