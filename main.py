#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import threading
import time
import webview
from resource_path import resource_path

# 导入app.py中的Flask应用
from app import app, socketio, get_local_ip, exit_event

# 全局变量
server_running = False
window = None
server_thread = None

# 运行Flask服务器
def run_server():
    global server_running
    server_running = True
    
    # 确保上传目录存在
    uploads_dir = resource_path('uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # 启动服务器
    print(f"\n文件快传已启动!")
    print(f"请访问: http://{get_local_ip()}:5000")
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"服务器异常: {e}")
    finally:
        server_running = False

# 安全停止服务器
def stop_server():
    global server_running, server_thread
    
    if server_running:
        print('\n正在停止服务器...')
        server_running = False
        # 设置退出事件
        exit_event.set()

# 关闭应用时的处理函数
def on_closing():
    stop_server()

# 创建webview窗口
def create_window():
    global window
    server_url = f"http://{get_local_ip()}:5000"
    # 注意这里窗口标题和尺寸可以根据需要调整
    window = webview.create_window('文件快传', server_url, width=900, height=700)
    webview.start(on_closing)

# 主函数
def main():
    # 启动服务器线程
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    # 创建WebView窗口
    create_window()

if __name__ == '__main__':
    main() 