#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
import time
import webview
from resource_path import resource_path

# 导入app.py中的Flask应用
from app import app, socketio, get_local_ip, exit_event, start_scheduler

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

    # 确保临时目录存在
    temp_chunks_dir = os.path.join(uploads_dir, '.temp_chunks')
    os.makedirs(temp_chunks_dir, exist_ok=True)

    # 启动服务器
    print(f"\n文件快传已启动!")
    print(f"请访问: http://{get_local_ip()}:5000")

    try:
        # 尝试启动服务器，如果端口被占用，尝试其他端口
        port = 5000
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
                break
            except OSError as e:
                if "Address already in use" in str(e) and attempt < max_attempts - 1:
                    print(f"端口 {port} 已被占用，尝试端口 {port+1}")
                    port += 1
                else:
                    raise
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

    # 获取服务器URL
    server_url = f"http://{get_local_ip()}:5000"

    # 设置窗口标题和图标
    title = '文件快传'
    icon_path = resource_path(os.path.join('static', 'app_icon.png'))

    # 检查图标是否存在
    if not os.path.exists(icon_path):
        print(f"警告: 图标文件不存在: {icon_path}")
        icon_path = None

    try:
        # 创建窗口
        window = webview.create_window(
            title=title,
            url=server_url,
            width=900,
            height=700,
            min_size=(800, 600),
            text_select=True,  # 允许文本选择
            easy_drag=True,    # 允许拖放文件
            zoomable=True      # 允许缩放
        )

        # 启动webview
        webview.start(on_closing)
        return True
    except Exception as e:
        print(f"创建窗口时出错: {e}")
        # 如果创建窗口失败，仍然运行服务器
        print(f"服务器仍然在运行，请访问: {server_url}")
        return False

# 主函数
def main():
    try:
        # 设置异常处理
        import sys
        def handle_exception(exc_type, exc_value, exc_traceback):
            # 忽略 KeyboardInterrupt 异常
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # 输出异常信息
            print("\n程序发生未处理的异常:")
            import traceback
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            print("\n请尝试重启程序或联系开发者\n")

            # 等待用户确认
            input("按回车键退出...")
            sys.exit(1)

        # 设置全局异常处理器
        sys.excepthook = handle_exception

        # 启动临时文件清理调度器
        start_scheduler()

        # 启动服务器线程
        global server_thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # 等待服务器启动
        print("正在启动服务器...")
        wait_attempts = 5
        while wait_attempts > 0 and not server_running:
            time.sleep(0.5)
            wait_attempts -= 1

        if not server_running:
            print("警告: 服务器启动可能延迟")

        # 创建WebView窗口
        if not create_window():
            # 如果窗口创建失败，阻塞主线程直到用户手动终止
            try:
                while server_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("用户终止程序")
                stop_server()
    except Exception as e:
        print(f"程序启动时出错: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == '__main__':
    main()