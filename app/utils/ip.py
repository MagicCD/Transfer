#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import logging

# 创建日志对象
logger = logging.getLogger(__name__)

def get_local_ip():
    """获取本机 IP 地址
    
    Returns:
        str: 本机在网络中的IP地址，如果获取失败则返回127.0.0.1
    """
    try:
        # 创建一个临时套接字连接到一个公共 IP 地址，这样我们可以获取本机在网络中的 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.warning(f"获取本地IP地址失败: {str(e)}")
        return '127.0.0.1'  # 如果获取失败，返回本地回环地址
