#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心接口模块
定义系统中使用的抽象接口和协议
"""

from app.core.interfaces.file_storage import FileStorageInterface, ChunkStorageInterface
from app.core.interfaces.upload import UploadInterface, ChunkedUploadInterface

__all__ = [
    'FileStorageInterface',
    'ChunkStorageInterface',
    'UploadInterface',
    'ChunkedUploadInterface'
]
