#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import PyInstaller.__main__

# 应用名称
APP_NAME = "内网文件传输工具"
# 入口文件
ENTRY_POINT = "main.py" 

# 确保当前目录是项目根目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 删除可能存在的build和dist目录
for dir_name in ['build', 'dist']:
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

# 检查是否存在app_modified.py，如果存在则复制为app.py
if os.path.exists('app_modified.py'):
    print("发现app_modified.py，将其复制为app.py...")
    shutil.copy('app_modified.py', 'app.py')

# 准备PyInstaller参数
pyinstaller_args = [
    # 基本参数
    f"--name={APP_NAME}",
    "--onefile",                 # 打包为单个可执行文件
    "--noconfirm",               # 不确认覆盖
    "--clean",                   # 清理临时文件
    "--windowed",                # 隐藏控制台窗口
    
    # 添加钩子和数据文件
    "--add-data=templates;templates",  # 添加模板目录
    "--add-data=uploads;uploads",      # 添加上传目录
    
    # 必要的隐含导入
    "--hidden-import=flask",
    "--hidden-import=flask_socketio",
    "--hidden-import=engineio.async_drivers.threading",
    "--hidden-import=simple_websocket",
    "--hidden-import=webview",
    
    # WebSocket相关导入
    "--hidden-import=socketio",
    "--hidden-import=socketio.client",
    "--hidden-import=socketio.server",
    "--hidden-import=engineio",
    "--hidden-import=engineio.client",
    "--hidden-import=engineio.server",
    
    # 排除一些不必要的模块以减小体积
    "--exclude-module=tkinter",
    "--exclude-module=matplotlib",
    "--exclude-module=numpy",
    
    # 添加图标(如果有)
    # "--icon=icon.ico",
    
    # 入口点脚本
    ENTRY_POINT
]

# 检查是否存在static目录，如果存在则添加
if os.path.exists('static'):
    pyinstaller_args.insert(-1, "--add-data=static;static")

print(f"开始打包 {APP_NAME}...")
print(f"使用参数: {' '.join(pyinstaller_args)}")

# 执行PyInstaller
PyInstaller.__main__.run(pyinstaller_args)

print(f"\n打包完成! 生成的可执行文件位于 dist/{APP_NAME}.exe")
print("注意: 请确保在目标机器上已安装所需的Visual C++ Redistributable和WebView2运行时") 