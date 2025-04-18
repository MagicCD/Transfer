#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
import time
import webview
import logging
import sys
from typing import Optional, Tuple

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入应用
from app import create_app, exit_event, start_scheduler
from app.utils.ip import get_local_ip
from app.utils.resource import resource_path

class ApplicationManager:
    """应用程序管理器"""
    def __init__(self):
        self.server_running: bool = False
        self.window: Optional[webview.Window] = None
        self.server_thread: Optional[threading.Thread] = None
        self.app = None
        self.socketio = None

    def check_python_version(self) -> None:
        """检查Python版本兼容性"""
        py_version = sys.version_info
        if py_version.major > 3 or (py_version.major == 3 and py_version.minor > 13):
            logger.warning(f"警告: 当前 Python 版本为 {py_version.major}.{py_version.minor}.{py_version.micro}")
            logger.warning("此应用程序在 Python 3.8 至 3.13 版本测试通过，更高版本可能会有兼容性问题。")
            logger.warning("尝试继续运行...\n")

    def initialize_app(self) -> Tuple[bool, str]:
        """初始化应用程序"""
        try:
            self.app, self.socketio = create_app()
            return True, ""
        except Exception as e:
            return False, str(e)

    def run_server(self, port: int = 5000, max_attempts: int = 3) -> None:
        """运行服务器"""
        self.server_running = True
        logger.info(f"\n文件快传已启动!")
        logger.info(f"请访问: http://{get_local_ip()}:{port}")

        try:
            for attempt in range(max_attempts):
                try:
                    self.socketio.run(
                        self.app,
                        host='0.0.0.0',
                        port=port,
                        allow_unsafe_werkzeug=True
                    )
                    break
                except OSError as e:
                    if "Address already in use" in str(e) and attempt < max_attempts - 1:
                        logger.warning(f"端口 {port} 已被占用，尝试端口 {port+1}")
                        port += 1
                    else:
                        raise
        except Exception as e:
            logger.error(f"服务器异常: {e}")
        finally:
            self.server_running = False

    def create_window(self) -> bool:
        """创建WebView窗口"""
        server_url = f"http://{get_local_ip()}:5000"
        title = '文件快传'
        icon_path = resource_path(os.path.join('static', 'app_icon.png'))

        if not os.path.exists(icon_path):
            logger.warning(f"警告: 图标文件不存在: {icon_path}")
            icon_path = None

        try:
            self.window = webview.create_window(
                title=title,
                url=server_url,
                width=900,
                height=700,
                min_size=(800, 600),
                text_select=True,
                easy_drag=True,
                zoomable=True
            )
            return True
        except Exception as e:
            logger.error(f"创建窗口时出错: {e}")
            logger.info(f"服务器仍然在运行，请访问: {server_url}")
            return False

    def stop_server(self) -> None:
        """停止服务器"""
        if self.server_running:
            logger.info('\n正在停止服务器...')
            self.server_running = False
            exit_event.set()

    def run(self) -> None:
        """运行应用程序"""
        try:
            # 检查Python版本
            self.check_python_version()

            # 初始化应用
            success, error = self.initialize_app()
            if not success:
                logger.error(f"初始化应用失败: {error}")
                return

            # 启动临时文件清理调度器
            start_scheduler()

            # 启动服务器线程
            self.server_thread = threading.Thread(
                target=self.run_server,
                daemon=True
            )
            self.server_thread.start()

            # 等待服务器启动
            logger.info("正在启动服务器...")
            wait_attempts = 5
            while wait_attempts > 0 and not self.server_running:
                time.sleep(0.5)
                wait_attempts -= 1

            if not self.server_running:
                logger.warning("警告: 服务器启动可能延迟")

            # 创建并启动WebView窗口
            if self.create_window():
                webview.start(self.stop_server)
            else:
                # 如果窗口创建失败，保持服务器运行直到手动终止
                try:
                    while self.server_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("用户终止程序")
                    self.stop_server()

        except Exception as e:
            logger.error(f"程序启动时出错: {e}")
            import traceback
            traceback.print_exc()
            input("按回车键退出...")

def main():
    """主函数"""
    # 设置全局异常处理
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error("\n程序发生未处理的异常:")
        import traceback
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        logger.error("\n请尝试重启程序或联系开发者\n")
        input("按回车键退出...")
        sys.exit(1)

    sys.excepthook = handle_exception

    # 启动应用
    app_manager = ApplicationManager()
    app_manager.run()

if __name__ == '__main__':
    main()

