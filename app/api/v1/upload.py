#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
上传API模块
提供文件上传相关的API路由
"""

import os
import logging
import asyncio
from flask import request, jsonify

from app.core.file_transfer.transfer_manager import TransferManager
from app.services.upload.chunk import ChunkUploadService
from app.services.upload.validator import UploadValidatorService
from app.core.exceptions import api_error_handler, FileUploadError, ChunkUploadError
from app.services.cache.cache_service import get_files_info

# 创建日志对象
logger = logging.getLogger(__name__)

def register_routes(app, socketio):
    """注册上传相关路由
    
    Args:
        app: Flask应用实例
        socketio: Socket.IO实例
    """
    
    @app.route('/api/v1/upload', methods=['POST'])
    @api_error_handler
    def upload_file():
        """处理普通文件上传"""
        # 检查是否有文件部分
        if 'file' not in request.files:
            return jsonify(success=False, error='No file part')
        
        file = request.files['file']
        
        # 如果用户没有选择文件
        if file.filename == '':
            return jsonify(success=False, error='No selected file')
        
        # 使用ChunkUploadService检查文件大小
        file_size, need_chunked_upload = ChunkUploadService.check_file_size(file)
        
        # 如果需要分块上传，返回提示
        if need_chunked_upload:
            logger.info(f"文件 {file.filename} 大小为 {file_size} 字节，需要使用分块上传")
            return jsonify(
                success=False,
                error='Large file detected',
                use_chunked_upload=True,
                file_size=file_size,
                message='此文件大小超过50MB，需要使用分块上传'
            )
        
        # 保存文件（小于50MB的文件）
        filename = os.path.basename(file.filename)
        
        # 验证上传请求
        UploadValidatorService.validate_upload_request(filename, file.content_type)
        
        # 使用ChunkUploadService保存文件
        ChunkUploadService.save_file(file, filename)
        
        # 通知所有客户端文件已更新
        socketio.emit('files_updated', {'files': get_files_info(force_refresh=True)})
        return jsonify(success=True, filename=filename)
    
    @app.route('/api/v1/upload/chunk', methods=['POST'])
    @api_error_handler
    def upload_chunk():
        """处理分块上传"""
        # 获取参数
        chunk_number = int(request.form.get('chunk_number', 0))
        total_chunks = int(request.form.get('total_chunks', 0))
        filename = request.form.get('filename', '')
        
        # 检查参数
        if not filename or 'file' not in request.files:
            raise FileUploadError('Invalid request parameters')
        
        # 确保文件名安全
        filename = os.path.basename(filename)
        chunk = request.files['file']
        
        # 验证分块上传请求
        UploadValidatorService.validate_chunk_request(filename, chunk_number, total_chunks)
        
        # 读取块数据
        chunk_data = chunk.read()
        
        # 使用ChunkUploadService异步处理分块上传
        success, result = asyncio.run(ChunkUploadService.process_upload_chunk(filename, chunk_number, total_chunks, chunk_data))
        
        if success:
            # 如果状态为完成，通知所有客户端文件已更新
            if result.get('status') == 'completed':
                socketio.emit('files_updated', {'files': get_files_info(force_refresh=True)})
            
            return jsonify(success=True, filename=filename, status=result.get('status', 'chunk_uploaded'))
        else:
            # 如果是暂停状态，返回特定的暂停标记
            if result.get('paused'):
                return jsonify(success=False, error='Upload paused', paused=True)
            
            # 如果是合并失败，返回缺失块信息
            if result.get('merge_failed'):
                return jsonify(
                    success=False,
                    error='Failed to merge chunks',
                    merge_failed=True,
                    missing_chunks=result.get('missing_chunks', [])
                )
            
            raise FileUploadError(result.get('error', 'Unknown error'))
    
    @app.route('/api/v1/upload/<filename>/cancel', methods=['POST'])
    @api_error_handler
    def cancel_upload(filename):
        """取消文件上传并清理临时文件"""
        # 使用TransferManager取消上传
        success, result = TransferManager.cancel_upload(filename)
        
        if success:
            # 通知所有客户端上传状态已更新
            socketio.emit('upload_state_updated', {
                'filename': filename,
                'status': 'cancelled',
                'paused': False
            })
            
            return jsonify(
                success=True,
                message=result.get('message', f'已取消上传并清理临时文件: {filename}'),
                cleaned=result.get('cleaned', False)
            )
        else:
            raise FileUploadError(result.get('error', 'Failed to cancel upload'))
    
    @app.route('/api/v1/upload/<filename>/pause', methods=['POST'])
    @api_error_handler
    def pause_upload(filename):
        """暂停特定文件上传的API"""
        # 从请求获取当前块索引
        data = request.get_json() or {}
        chunk_index = data.get('chunk_index', 0)
        
        # 使用TransferManager暂停上传
        success = TransferManager.pause_upload(filename, chunk_index)
        
        # 通知所有客户端上传状态已更新
        from app.config import UPLOAD_STATUS
        socketio.emit('upload_state_updated', {
            'filename': filename,
            'status': UPLOAD_STATUS['PAUSED'],
            'chunk_index': chunk_index,
            'paused': True
        })
        
        if success:
            logger.info(f"暂停上传文件: {filename}, 当前块: {chunk_index}")
            return jsonify(success=True, message=f'已暂停上传: {filename}')
        else:
            raise FileUploadError('Failed to pause upload')
    
    @app.route('/api/v1/upload/<filename>/resume', methods=['POST'])
    @api_error_handler
    def resume_upload(filename):
        """恢复特定文件上传的API"""
        # 使用TransferManager恢复上传
        success, result = TransferManager.resume_upload(filename)
        
        if success:
            # 通知所有客户端上传状态已更新
            from app.config import UPLOAD_STATUS
            socketio.emit('upload_state_updated', {
                'filename': filename,
                'status': UPLOAD_STATUS['UPLOADING'],
                'chunk_index': result.get('last_chunk', 0),
                'paused': False,
                'has_temp_dir': result.get('has_temp_dir', False)
            })
            
            logger.info(f"恢复上传文件: {filename}, 从块 {result.get('last_chunk', 0)} 开始")
            return jsonify(
                success=True,
                message=result.get('message', f'已恢复上传: {filename}'),
                last_chunk=result.get('last_chunk', 0),
                has_temp_dir=result.get('has_temp_dir', False),
                cleaned_chunks=result.get('cleaned_chunks', 0)
            )
        else:
            raise FileUploadError(result.get('error', 'Failed to resume upload'))
    
    @app.route('/api/v1/upload/<filename>/state', methods=['GET'])
    @api_error_handler
    def get_upload_state(filename):
        """获取文件上传状态的API"""
        # 使用TransferManager获取上传状态
        state = TransferManager.get_upload_state(filename)
        return jsonify(state)
    
    # 为了向后兼容，保留旧的路由
    @app.route('/upload', methods=['POST'])
    @api_error_handler
    def upload_file_legacy():
        """处理普通文件上传（旧路由）"""
        return upload_file()
    
    @app.route('/upload/chunk', methods=['POST'])
    @api_error_handler
    def upload_chunk_legacy():
        """处理分块上传（旧路由）"""
        return upload_chunk()
    
    @app.route('/cancel_upload/<filename>', methods=['POST'])
    @api_error_handler
    def cancel_upload_legacy(filename):
        """取消文件上传并清理临时文件（旧路由）"""
        return cancel_upload(filename)
    
    @app.route('/pause_upload/<filename>', methods=['POST'])
    @api_error_handler
    def pause_upload_legacy(filename):
        """暂停特定文件上传的API（旧路由）"""
        return pause_upload(filename)
    
    @app.route('/resume_upload/<filename>', methods=['POST'])
    @api_error_handler
    def resume_upload_legacy(filename):
        """恢复特定文件上传的API（旧路由）"""
        return resume_upload(filename)
    
    @app.route('/upload_state/<filename>', methods=['GET'])
    @api_error_handler
    def get_upload_state_legacy(filename):
        """获取文件上传状态的API（旧路由）"""
        return get_upload_state(filename)
