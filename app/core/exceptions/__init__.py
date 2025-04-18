#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
异常处理模块
定义应用程序中使用的自定义异常类和异常处理机制
"""

from app.core.exceptions.base import (
    FileTransferError,
    FileNotFoundError,
    FileUploadError,
    ChunkUploadError,
    FileMergeError,
    FileDeleteError,
    ConfigurationError,
    UploadCancelledError,
    UploadPausedError
)

from app.core.exceptions.handler import (
    handle_error,
    api_error_handler,
    register_error_handlers
)

__all__ = [
    # 异常类
    'FileTransferError',
    'FileNotFoundError',
    'FileUploadError',
    'ChunkUploadError',
    'FileMergeError',
    'FileDeleteError',
    'ConfigurationError',
    'UploadCancelledError',
    'UploadPausedError',

    # 异常处理
    'handle_error',
    'api_error_handler',
    'register_error_handlers'
]
