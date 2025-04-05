#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和PyInstaller打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的临时目录路径
        base_path = sys._MEIPASS
    else:
        # 开发环境下的当前目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path) 