#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基础异常类模块
定义应用程序中使用的所有自定义异常类
"""

class FileTransferError(Exception):
    """文件传输应用基础异常类"""
    def __init__(self, message="文件传输操作失败", code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class FileNotFoundError(FileTransferError):
    """文件不存在异常"""
    def __init__(self, filename=None):
        message = f"文件不存在: {filename}" if filename else "请求的文件不存在"
        super().__init__(message=message, code=404)


class FileUploadError(FileTransferError):
    """文件上传异常"""
    def __init__(self, message="文件上传失败", code=400):
        super().__init__(message=message, code=code)


class ChunkUploadError(FileUploadError):
    """分块上传异常"""
    def __init__(self, message="文件分块上传失败", chunk_number=None, filename=None):
        if chunk_number is not None and filename is not None:
            message = f"文件 {filename} 的第 {chunk_number} 块上传失败"
        super().__init__(message=message, code=400)


class FileMergeError(FileUploadError):
    """文件合并异常"""
    def __init__(self, message="文件合并失败", filename=None, missing_chunks=None):
        if filename:
            message = f"文件 {filename} 合并失败"
        if missing_chunks:
            message += f"，缺少块: {missing_chunks}"
        super().__init__(message=message, code=400)


class FileDeleteError(FileTransferError):
    """文件删除异常"""
    def __init__(self, filename=None):
        message = f"删除文件失败: {filename}" if filename else "删除文件失败"
        super().__init__(message=message, code=400)


class ConfigurationError(FileTransferError):
    """配置错误异常"""
    def __init__(self, message="配置错误"):
        super().__init__(message=message, code=500)


class UploadCancelledError(FileUploadError):
    """上传取消异常"""
    def __init__(self, filename=None):
        message = f"上传已取消: {filename}" if filename else "上传已取消"
        super().__init__(message=message, code=400)


class UploadPausedError(FileUploadError):
    """上传暂停异常"""
    def __init__(self, filename=None):
        message = f"上传已暂停: {filename}" if filename else "上传已暂停"
        super().__init__(message=message, code=400)
