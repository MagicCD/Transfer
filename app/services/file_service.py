#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from app.config import (
    UPLOAD_FOLDER, TEMP_CHUNKS_DIR, TEMP_FILES_MAX_AGE, UPLOAD_STATUS
)
from app.services.common import get_file_icon, format_file_size

# 创建日志对象
logger = logging.getLogger(__name__)

# 使用字典存储上传状态信息
# {filename: {
#     'status': UPLOAD_STATUS['UPLOADING'],  # 当前状态
#     'last_chunk': 12,                      # 最后上传的块索引
#     'total_chunks': 100,                   # 总块数
#     'timestamp': datetime.now(),           # 最后更新时间
#     'error': None,                         # 错误信息
#     'uploaded_chunks': set(),              # 已上传的块集合
#     'failed_chunks': set()                 # 上传失败的块集合
# }}
upload_states = {}

# 文件图标处理相关函数已移至common.py

# 文件大小格式化相关函数已移至common.py

# 删除部分写入的文件
def remove_partial_file(file_path):
    """删除部分写入的文件，避免损坏文件残留

    Args:
        file_path (str): 文件路径

    Returns:
        bool: 是否成功删除
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

# 清理指定文件的损坏块
def clean_corrupted_chunks(filename, corrupted_chunk_indices=None):
    """清理指定文件的损坏块

    Args:
        filename (str): 文件名
        corrupted_chunk_indices (list): 损坏块的索引列表，如果为None，则检查所有块

    Returns:
        tuple: (清理的块数, 损坏块列表)
    """
    try:
        file_temp_dir = os.path.join(TEMP_CHUNKS_DIR, filename)
        if not os.path.exists(file_temp_dir):
            logger.warning(f"文件的临时目录不存在: {filename}")
            return 0, []

        cleaned_count = 0
        corrupted_chunks = []

        # 如果指定了损坏块索引，只清理这些块
        if corrupted_chunk_indices:
            for i in corrupted_chunk_indices:
                # 删除所有匹配的块文件
                for chunk_file in os.listdir(file_temp_dir):
                    if chunk_file.startswith(f"chunk_{i}_"):
                        chunk_path = os.path.join(file_temp_dir, chunk_file)
                        try:
                            os.remove(chunk_path)
                            cleaned_count += 1
                            if i not in corrupted_chunks:
                                corrupted_chunks.append(i)
                            logger.info(f"删除损坏块: {chunk_path}")
                        except Exception as e:
                            logger.error(f"删除损坏块时出错: {chunk_path}, {str(e)}")
        else:
            # 检查所有块，分析块的完整性
            # 首先收集所有块索引
            chunk_indices = set()
            for chunk_file in os.listdir(file_temp_dir):
                if chunk_file.startswith("chunk_") and "_" in chunk_file:
                    try:
                        chunk_index = int(chunk_file.split("_")[1])
                        chunk_indices.add(chunk_index)
                    except (ValueError, IndexError):
                        pass

            # 检查每个块索引的文件是否完整
            for chunk_index in chunk_indices:
                # 获取该块索引的所有文件
                chunk_files = [f for f in os.listdir(file_temp_dir) if f.startswith(f"chunk_{chunk_index}_")]

                # 如果有多个文件匹配同一个块索引，只保留最新的一个
                if len(chunk_files) > 1:
                    # 按修改时间排序
                    chunk_files.sort(key=lambda f: os.path.getmtime(os.path.join(file_temp_dir, f)), reverse=True)

                    # 删除旧文件
                    for old_file in chunk_files[1:]:
                        old_path = os.path.join(file_temp_dir, old_file)
                        try:
                            os.remove(old_path)
                            cleaned_count += 1
                            logger.info(f"删除重复块文件: {old_path}")
                        except Exception as e:
                            logger.error(f"删除重复块文件时出错: {old_path}, {str(e)}")

        return cleaned_count, corrupted_chunks
    except Exception as e:
        logger.error(f"清理损坏块时出错: {str(e)}")
        return 0, []

# 清理过期的临时文件
def clean_temp_files():
    """清理过期的临时文件和上传状态"""
    try:
        temp_dir = TEMP_CHUNKS_DIR
        if not os.path.exists(temp_dir):
            return

        current_time = datetime.now()
        max_age = timedelta(hours=TEMP_FILES_MAX_AGE)

        # 遍历临时目录中的所有文件
        for dirname in os.listdir(temp_dir):
            dir_path = os.path.join(temp_dir, dirname)
            if not os.path.isdir(dir_path):
                continue

            # 获取文件夹的修改时间
            dir_modified_time = datetime.fromtimestamp(os.path.getmtime(dir_path))

            # 如果文件夹超过最大保留时间，则删除
            if current_time - dir_modified_time > max_age:
                logger.info(f"清理过期临时分块: {dirname}")
                shutil.rmtree(dir_path)
    except Exception as e:
        logger.error(f"清理临时文件时出错: {str(e)}")

    # 清理过期的上传状态信息
    try:
        # 创建要删除的键列表
        keys_to_delete = []

        # 检查所有上传状态
        for filename, state in upload_states.items():
            # 获取状态的最后更新时间
            last_update = state.get('timestamp')
            if last_update and (current_time - last_update > max_age):
                keys_to_delete.append(filename)

        # 删除过期的状态信息
        for key in keys_to_delete:
            logger.info(f"清理过期上传状态: {key}")
            upload_states.pop(key, None)

    except Exception as e:
        logger.error(f"清理上传状态时出错: {str(e)}")

# 计算文件块的MD5哈希值
def calculate_chunk_hash(chunk_data):
    """计算数据块的MD5哈希值

    Args:
        chunk_data (bytes): 数据块内容

    Returns:
        str: MD5哈希值
    """
    return hashlib.md5(chunk_data).hexdigest()

# 生成基于哈希的块文件名
def get_chunk_filename(chunk_number, chunk_hash):
    """生成包含哈希值的块文件名，便于验证和重复数据检测

    Args:
        chunk_number (int): 块编号
        chunk_hash (str): 块的哈希值

    Returns:
        str: 块文件名
    """
    return f"chunk_{chunk_number}_{chunk_hash}"

async def merge_chunks_async(file_temp_dir, final_path, total_chunks):
    """使用流式处理合并文件块，避免高内存消耗

    Args:
        file_temp_dir (str): 临时块目录
        final_path (str): 最终文件路径
        total_chunks (int): 总块数

    Returns:
        bool: 是否成功合并
    """
    start_time = time.time()
    logger.info(f"开始合并文件块，总块数: {total_chunks}，目标文件: {final_path}")

    # 检查所有块是否存在
    missing_chunks = []
    chunk_files = {}  # 存储每个块索引对应的文件路径

    # 首先收集所有块文件
    for filename in os.listdir(file_temp_dir):
        if filename.startswith("chunk_") and "_" in filename:
            try:
                # 从文件名中提取块索引
                chunk_index = int(filename.split('_')[1])
                chunk_files[chunk_index] = os.path.join(file_temp_dir, filename)
            except (ValueError, IndexError):
                logger.warning(f"无法解析块文件名: {filename}")

    # 检查是否有缺失的块
    for i in range(total_chunks):
        if i not in chunk_files:
            missing_chunks.append(i)

    if missing_chunks:
        logger.error(f"合并失败: 缺少以下块: {missing_chunks}")
        return False

    try:
        # 创建最终文件
        async with aiofiles.open(final_path, 'wb') as outfile:
            total_bytes_written = 0

            # 按顺序处理每个块
            for i in range(total_chunks):
                chunk_file_path = chunk_files[i]

                # 直接流式读取并写入块数据
                async with aiofiles.open(chunk_file_path, 'rb') as chunk_file:
                    # 使用缓冲区读取并写入，避免将整个块加载到内存
                    buffer_size = 1024 * 1024  # 1MB缓冲区
                    bytes_written = 0

                    while True:
                        buffer = await chunk_file.read(buffer_size)
                        if not buffer:
                            break

                        await outfile.write(buffer)
                        bytes_written += len(buffer)
                        total_bytes_written += len(buffer)

                # 每处理10个块或处理完最后一个块时报告进度
                if (i + 1) % 10 == 0 or i == total_chunks - 1:
                    progress = ((i + 1) / total_chunks) * 100
                    logger.info(f"合并进度: {progress:.1f}%, 已写入: {format_file_size(total_bytes_written)}")

                # 定期强制垃圾回收
                if (i + 1) % 50 == 0:
                    gc.collect()

        # 验证最终文件大小
        final_size = os.path.getsize(final_path)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"文件合并完成，大小: {format_file_size(final_size)}，耗时: {duration:.2f}秒")

        return True
    except Exception as e:
        logger.error(f"异步合并文件块时出错: {str(e)}")
        # 删除部分写入的文件
        remove_partial_file(final_path)
        return False

async def process_chunk(chunk_file_path, chunk_index, chunk_data):
    """异步处理单个分块 - 保留用于兼容性

    Args:
        chunk_file_path (str): 块文件路径
        chunk_index (int): 块索引
        chunk_data (dict): 存储块数据的字典
    """
    try:
        # 获取文件大小
        file_size = os.path.getsize(chunk_file_path)

        # 对于小文件，直接读取而不使用内存映射
        if file_size < 1024 * 1024:  # 小于1MB的文件
            async with aiofiles.open(chunk_file_path, 'rb') as infile:
                chunk_content = await infile.read()
                # 计算块的MD5校验和
                chunk_hash = hashlib.md5(chunk_content).hexdigest()

                # 检查是否已经上传过这个块
                chunk_hash_file = f"{chunk_file_path}.hash"
                if os.path.exists(chunk_hash_file):
                    with open(chunk_hash_file, 'r') as hash_file:
                        existing_hash = hash_file.read().strip()
                        if existing_hash == chunk_hash:
                            # 块已经上传过，使用空数据替代
                            chunk_data[chunk_index] = b''
                            return

                # 保存块的校验和
                async with aiofiles.open(chunk_hash_file, 'w') as hash_file:
                    await hash_file.write(chunk_hash)

                # 存储数据
                chunk_data[chunk_index] = chunk_content
        else:
            # 对于大文件，使用内存映射
            with open(chunk_file_path, 'rb') as infile:
                with mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # 计算块的MD5校验和
                    chunk_hash = hashlib.md5(mm).hexdigest()

                    # 检查是否已经上传过这个块
                    chunk_hash_file = f"{chunk_file_path}.hash"
                    if os.path.exists(chunk_hash_file):
                        with open(chunk_hash_file, 'r') as hash_file:
                            existing_hash = hash_file.read().strip()
                            if existing_hash == chunk_hash:
                                # 块已经上传过，使用空数据替代
                                chunk_data[chunk_index] = b''
                                return

                    # 保存块的校验和
                    with open(chunk_hash_file, 'w') as hash_file:
                        hash_file.write(chunk_hash)

                    # 读取数据并存储在字典中
                    chunk_data[chunk_index] = mm.read()
    except Exception as e:
        logger.error(f"处理分块 {chunk_index} 时出错: {str(e)}")
        # 放入空数据以保持索引完整性
        chunk_data[chunk_index] = b''

async def process_chunk_streaming(chunk_file_path, chunk_index, outfile):
    """流式处理单个分块并直接写入输出文件，避免高内存消耗

    Args:
        chunk_file_path (str): 块文件路径
        chunk_index (int): 块索引
        outfile: 输出文件对象

    Returns:
        int: 写入的字节数
    """
    try:
        # 获取文件大小
        file_size = os.path.getsize(chunk_file_path)
        if file_size == 0:
            logger.warning(f"分块 {chunk_index} 大小为0，跳过")
            return 0

        # 检查是否已经上传过这个块
        chunk_hash_file = f"{chunk_file_path}.hash"
        chunk_hash = None

        # 对于小文件，直接读取并处理
        if file_size < 1024 * 1024:  # 小于1MB的文件
            async with aiofiles.open(chunk_file_path, 'rb') as infile:
                chunk_content = await infile.read()
                # 计算块的MD5校验和
                chunk_hash = hashlib.md5(chunk_content).hexdigest()

                # 检查是否已经上传过这个块
                if os.path.exists(chunk_hash_file):
                    with open(chunk_hash_file, 'r') as hash_file:
                        existing_hash = hash_file.read().strip()
                        if existing_hash == chunk_hash:
                            # 块已经上传过，跳过写入
                            return 0

                # 直接写入数据到输出文件
                await outfile.write(chunk_content)

                # 保存块的校验和
                async with aiofiles.open(chunk_hash_file, 'w') as hash_file:
                    await hash_file.write(chunk_hash)

                return len(chunk_content)
        else:
            # 对于大文件，使用内存映射并分块读取写入
            with open(chunk_file_path, 'rb') as infile:
                # 首先计算MD5校验和
                with mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    chunk_hash = hashlib.md5(mm).hexdigest()

                    # 检查是否已经上传过这个块
                    if os.path.exists(chunk_hash_file):
                        with open(chunk_hash_file, 'r') as hash_file:
                            existing_hash = hash_file.read().strip()
                            if existing_hash == chunk_hash:
                                # 块已经上传过，跳过写入
                                return 0

                    # 分块读取并写入，避免一次性加载整个文件到内存
                    # 重置内存映射位置
                    mm.seek(0)

                    # 使用较小的缓冲区分块读取和写入
                    buffer_size = 1024 * 1024  # 1MB缓冲区
                    bytes_written = 0

                    while True:
                        buffer = mm.read(buffer_size)
                        if not buffer:
                            break

                        await outfile.write(buffer)
                        bytes_written += len(buffer)

                    # 保存块的校验和
                    with open(chunk_hash_file, 'w') as hash_file:
                        hash_file.write(chunk_hash)

                    return bytes_written
    except Exception as e:
        logger.error(f"流式处理分块 {chunk_index} 时出错: {str(e)}")
        return 0
