#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import platform
import shutil

def install_requirements():
    print("安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("批量安装失败，尝试单独安装...")
        with open("requirements.txt", "r") as f:
            requirements = f.read().splitlines()
        
        for req in requirements:
            try:
                print(f"正在安装 {req}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            except subprocess.CalledProcessError:
                print(f"警告: 安装 {req} 失败，但将继续安装其他依赖")
    
    print("安装 PyInstaller...")
    try:
        # 尝试使用不指定版本
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    except subprocess.CalledProcessError:
        print("PyInstaller安装失败，请手动安装")
        return False
    return True

def build_executable():
    print("构建可执行文件...")
    
    # 检查是否存在 uploads 目录，如果不存在则创建
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    
    # 简化的构建命令
    cmd = [
        "pyinstaller",
        "--name=内网文件传输工具",
        "--add-data=templates;templates" if platform.system() == "Windows" else "--add-data=templates:templates",
        "--hidden-import=flask",
        "--hidden-import=flask_socketio",
        "--hidden-import=simple_websocket",
        "--hidden-import=engineio.async_drivers.threading",
        "--hidden-import=webview",
        "--hidden-import=webview.platforms.winforms" if platform.system() == "Windows" else "",
        "--noconsole",
        "--onedir",
        "--clean",
        "app.py"
    ]
    
    # 移除空选项
    cmd = [item for item in cmd if item]
    
    print("执行PyInstaller命令...")
    for item in cmd:
        print(f"  {item}")
    
    try:
        subprocess.check_call(cmd)
        print("PyInstaller编译成功!")
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller编译失败: {e}")
        return False
    
    # 复制 uploads 目录到可执行文件目录
    dest_dir = os.path.join("dist", "内网文件传输工具", "uploads")
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    shutil.copytree("uploads", dest_dir)
    
    print("\n构建完成！")
    
    # 打印可执行文件路径
    if platform.system() == "Windows":
        exe_path = os.path.abspath(os.path.join("dist", "内网文件传输工具", "内网文件传输工具.exe"))
        print(f"可执行文件位置: {exe_path}")
    else:
        exe_path = os.path.abspath(os.path.join("dist", "内网文件传输工具", "内网文件传输工具"))
        print(f"可执行文件位置: {exe_path}")
    
    print("\n注意：")
    print("1. 第一次打开时，可能会被防火墙拦截，请允许访问")
    print("2. 如需在其他电脑上使用，需将整个 dist/内网文件传输工具 目录复制过去")
    return True

if __name__ == "__main__":
    if install_requirements():
        if build_executable():
            print("\n程序构建完成，按任意键退出...")
        else:
            print("\n程序构建失败，请检查错误并重试...")
    else:
        print("\n安装依赖失败，无法构建程序...")
    
    # 在Windows上等待用户按键
    if platform.system() == "Windows":
        os.system("pause") 