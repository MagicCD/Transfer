#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件存储服务
负责文件的存储、删除等基本操作
"""

import os
import logging
import shutil
import hashlib
import mmap
import asyncio
import aiofiles
import gc
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Union, Set, BinaryIO

from app.config import (
    UPLOAD_FOLDER, TEMP_CHUNKS_DIR, TEMP_FILES_MAX_AGE
)
from app.services.cache.cache_service import invalidate_files_cache
from app.core.exceptions import FileNotFoundError, FileDeleteError, FileMergeError

# 创建日志对象
logger = logging.getLogger(__name__)

class StorageService:
    """文件存储服务类，处理文件的基本存储操作"""
    
    @staticmethod
    def get_file_path(filename: str) -> str:
        """获取文件的完整路径
        
        Args:
            filename: 文件名
            
        Returns:
            文件的完整路径
        """
        return os.path.join(UPLOAD_FOLDER, filename)
    
    @staticmethod
    def delete_file(filename: str) -> bool:
        """删除单个文件
        
        Args:
            filename: 要删除的文件名
            
        Returns:
            是否成功删除
            
        Raises:
            FileNotFoundError: 当文件不存在时
            FileDeleteError: 当删除文件失败时
        """
        try:
            file_path = StorageService.get_file_path(filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"文件已删除: {filename}")
                
                # 使缓存失效
                invalidate_files_cache()
                
                return True
            else:
                logger.warning(f"尝试删除不存在的文件: {filename}")
                raise FileNotFoundError(filename)
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除文件时出错: {str(e)}")
            raise FileDeleteError(filename)
    
    @staticmethod
    def delete_all_files() -> Tuple[bool, int]:
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
            logger.info(f"删除了 {deleted_count} 个文件, 删除前: {files_before}, 删除后: {len(StorageService.get_files_list())}")
            
            return True, deleted_count
        except Exception as e:
            logger.error(f"删除所有文件时出错: {str(e)}")
            return False, 0
    
    @staticmethod
    def get_files_list() -> List[str]:
        """获取所有文件名列表
        
        Returns:
            文件名列表
        """
        if not os.path.exists(UPLOAD_FOLDER):
            return []
        
        return [f for f in os.listdir(UPLOAD_FOLDER) 
                if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    
    @staticmethod
    def clean_temp_files() -> None:
        """清理过期的临时文件和上传状态"""
        try:
            # 获取当前时间
            now = datetime.now()
            
            # 清理过期的临时分块目录
            if os.path.exists(TEMP_CHUNKS_DIR):
                for dirname in os.listdir(TEMP_CHUNKS_DIR):
                    dir_path = os.path.join(TEMP_CHUNKS_DIR, dirname)
                    if os.path.isdir(dir_path):
                        # 检查目录的修改时间
                        modified_time = datetime.fromtimestamp(os.path.getmtime(dir_path))
                        age_hours = (now - modified_time).total_seconds() / 3600
                        
                        # 如果目录超过最大保存时间，删除它
                        if age_hours > TEMP_FILES_MAX_AGE:
                            try:
                                shutil.rmtree(dir_path)
                                logger.info(f"已清理过期的临时分块目录: {dirname}, 年龄: {age_hours:.2f}小时")
                            except Exception as e:
                                logger.error(f"清理临时分块目录时出错: {str(e)}")
            
            # 清理上传状态中的过期记录
            from app.core.file_transfer.transfer_manager import upload_states
            expired_files = []
            
            for filename, state in upload_states.items():
                if 'timestamp' in state:
                    last_update = state['timestamp']
                    age_hours = (now - last_update).total_seconds() / 3600
                    
                    # 如果状态超过最大保存时间，标记为过期
                    if age_hours > TEMP_FILES_MAX_AGE:
                        expired_files.append(filename)
            
            # 删除过期的状态记录
            for filename in expired_files:
                if filename in upload_states:
                    del upload_states[filename]
                    logger.info(f"已清理过期的上传状态记录: {filename}")
            
            logger.info(f"临时文件清理完成，清理了 {len(expired_files)} 个过期状态记录")
        except Exception as e:
            logger.error(f"清理临时文件时出错: {str(e)}")

# 文件块处理相关函数

def remove_partial_file(file_path: str) -> bool:
    """删除部分写入的文件，避免损坏文件残留
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否成功删除
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"已删除部分写入的文件: {file_path}")
            return True
        except Exception as del_error:
            logger.error(f"无法删除部分写入的文件: {str(del_error)}")
            return False
    return False

def calculate_chunk_hash(chunk_data: bytes) -> str:
    """计算数据块的MD5哈希值
    
    Args:
        chunk_data: 数据块内容
        
    Returns:
        MD5哈希值
    """
    return hashlib.md5(chunk_data).hexdigest()

def get_chunk_filename(chunk_number: int, chunk_hash: str) -> str:
    """生成包含哈希值的块文件名，便于验证和重复数据检测
    
    Args:
        chunk_number: 块编号
        chunk_hash: 块的哈希值
        
    Returns:
        块文件名
    """
    return f"chunk_{chunk_number}_{chunk_hash}"

def clean_corrupted_chunks(filename: str, corrupted_chunk_indices: Optional[List[int]] = None) -> Tuple[int, List[int]]:
    """清理指定文件的损坏块
    
    Args:
        filename: 文件名
        corrupted_chunk_indices: 损坏块的索引列表，如果为None，则检查所有块
        
    Returns:
        tuple: (清理的块数, 损坏块列表)
    """
    file_temp_dir = os.path.join(TEMP_CHUNKS_DIR, filename)
    cleaned_count = 0
    corrupted_chunks = []
    
    if not os.path.exists(file_temp_dir):
        return 0, []
    
    try:
        # 如果提供了损坏块索引，只清理这些块
        if corrupted_chunk_indices:
            for chunk_index in corrupted_chunk_indices:
                # 查找匹配的块文件
                for chunk_file in os.listdir(file_temp_dir):
                    if chunk_file.startswith(f"chunk_{chunk_index}_"):
                        chunk_path = os.path.join(file_temp_dir, chunk_file)
                        try:
                            os.remove(chunk_path)
                            cleaned_count += 1
                            corrupted_chunks.append(chunk_index)
                            logger.info(f"已清理损坏的块: {chunk_file}")
                        except Exception as e:
                            logger.error(f"清理损坏块时出错: {str(e)}")
        else:
            # 如果没有提供损坏块索引，检查所有块的完整性
            # 这里可以实现更复杂的块验证逻辑
            pass
        
        return cleaned_count, corrupted_chunks
    except Exception as e:
        logger.error(f"清理损坏块时出错: {str(e)}")
        return 0, []

async def process_chunk(chunk_file_path: str, chunk_index: int, chunk_data: Dict[int, bytes]) -> None:
    """异步处理单个分块 - 保留用于兼容性
    
    Args:
        chunk_file_path: 块文件路径
        chunk_index: 块索引
        chunk_data: 存储块数据的字典
    """
    try:
        # 读取块文件
        async with aiofiles.open(chunk_file_path, 'rb') as f:
            chunk_data[chunk_index] = await f.read()
    except Exception as e:
        logger.error(f"读取块文件时出错: {str(e)}")
        chunk_data[chunk_index] = b''  # 设置为空字节，表示读取失败

async def process_chunk_streaming(chunk_file_path: str, chunk_index: int, outfile) -> int:
    """流式处理单个分块并直接写入输出文件，避免高内存消耗
    
    Args:
        chunk_file_path: 块文件路径
        chunk_index: 块索引
        outfile: 输出文件对象
        
    Returns:
        写入的字节数
    """
    try:
        # 读取块文件并直接写入输出文件
        bytes_written = 0
        async with aiofiles.open(chunk_file_path, 'rb') as f:
            # 使用较小的缓冲区读取和写入，避免一次性加载整个块到内存
            buffer_size = 64 * 1024  # 64KB缓冲区
            while True:
                chunk = await f.read(buffer_size)
                if not chunk:
                    break
                outfile.write(chunk)
                bytes_written += len(chunk)
                # 强制刷新写入
                outfile.flush()
                
                # 主动触发垃圾回收，减少内存压力
                if bytes_written % (1024 * 1024) == 0:  # 每写入1MB
                    gc.collect()
        
        return bytes_written
    except Exception as e:
        logger.error(f"流式处理块文件时出错: {str(e)}")
        return 0

async def merge_chunks_async(file_temp_dir: str, final_path: str, total_chunks: int) -> bool:
    """使用流式处理合并文件块，避免高内存消耗
    
    Args:
        file_temp_dir: 临时块目录
        final_path: 最终文件路径
        total_chunks: 总块数
        
    Returns:
        是否成功合并
    """
    try:
        # 检查临时目录是否存在
        if not os.path.exists(file_temp_dir):
            logger.error(f"临时目录不存在: {file_temp_dir}")
            raise FileMergeError(message="临时目录不存在")
        
        # 检查是否有足够的块
        chunk_files = os.listdir(file_temp_dir)
        if len(chunk_files) < total_chunks:
            logger.error(f"块数量不足: 预期 {total_chunks}, 实际 {len(chunk_files)}")
            
            # 找出缺失的块
            missing_chunks = []
            for i in range(total_chunks):
                found = False
                for chunk_file in chunk_files:
                    if chunk_file.startswith(f"chunk_{i}_"):
                        found = True
                        break
                if not found:
                    missing_chunks.append(i)
            
            raise FileMergeError(message="块数量不足", filename=os.path.basename(final_path), missing_chunks=missing_chunks)
        
        # 创建输出文件
        with open(final_path, 'wb') as outfile:
            # 按顺序处理每个块
            for chunk_index in range(total_chunks):
                # 查找匹配的块文件
                chunk_file_path = None
                for chunk_file in chunk_files:
                    if chunk_file.startswith(f"chunk_{chunk_index}_"):
                        chunk_file_path = os.path.join(file_temp_dir, chunk_file)
                        break
                
                if not chunk_file_path:
                    logger.error(f"找不到块 {chunk_index}")
                    raise FileMergeError(message=f"找不到块 {chunk_index}", filename=os.path.basename(final_path))
                
                # 流式处理块并写入输出文件
                bytes_written = await process_chunk_streaming(chunk_file_path, chunk_index, outfile)
                
                if bytes_written == 0:
                    logger.error(f"处理块 {chunk_index} 时出错")
                    raise FileMergeError(message=f"处理块 {chunk_index} 时出错", filename=os.path.basename(final_path))
                
                # 主动触发垃圾回收，减少内存压力
                gc.collect()
        
        logger.info(f"文件合并成功: {final_path}")
        return True
    except FileMergeError:
        # 删除部分写入的文件
        remove_partial_file(final_path)
        raise
    except Exception as e:
        logger.error(f"合并文件块时出错: {str(e)}")
        # 删除部分写入的文件
        remove_partial_file(final_path)
        raise FileMergeError(message=str(e), filename=os.path.basename(final_path))
