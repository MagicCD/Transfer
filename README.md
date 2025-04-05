# LAN File Transfer Tool

[中文文档](#内网文件传输工具)

A simple and easy-to-use LAN file transfer tool that allows quick file transfers within a local network, supporting multiple file uploads simultaneously.

## Features

- Simple and intuitive interface
- Support for multiple file uploads (up to 1GB)
- Drag and drop file upload
- Real-time upload progress display
- Direct file download or deletion (supports batch deletion)
- Automatic display of different file type icons
- File size information display
- Can be packaged as an executable file, no Python environment required

## System Requirements

- Windows (tested on Windows 10/11)
- Python 3.8 - 3.13 (compatibility issues with Python 3.13 have been resolved)

## Dependencies

- flask==2.3.3
- flask-socketio==5.3.4
- pywebview==4.3
- simple-websocket==1.0.0
- Werkzeug==2.3.7
- pyinstaller==6.12.0

## Usage

### Method 1: Run Python Script Directly

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app.py`
3. The program will automatically open a window displaying the file transfer interface

### Method 2: Use Executable File

1. Run the build script: `python build_exe.py` or `build.bat`
2. Wait for the build to complete
3. Find the executable file in the `dist/内网文件传输工具` directory
4. Double-click to run the executable file, which will open a window displaying the file transfer interface

## Python 3.13 Compatibility Note

This project is fully compatible with Python 3.13, using threading mode to run Flask-SocketIO and pywebview as a unified interface to create a standalone application window. All dependencies have been tested for compatibility.

## Build Notes

When building the executable file:
- Uses PyInstaller 6.12.0 for packaging, automatically configuring required dependencies and imports
- Uses single directory mode (--onedir) for packaging, generating a standalone application directory
- Automatically installs all dependencies in requirements.txt
- Automatically creates and configures the uploads directory
- Uses threading mode to run Flask-SocketIO, avoiding gevent compatibility issues
- Supports Windows systems, automatically obtains the local IP address
- Supports Python 3.8 to 3.13 versions, automatically checks version compatibility
- Fully automated build process, no manual configuration required

## Notes

1. The program will create an `uploads` folder in the current directory to store uploaded files
2. The first time you run it, it may be blocked by the firewall, please allow access
3. If you need to run the generated exe file on another computer, you need to copy the entire `dist/内网文件传输工具` directory
4. Close the window to completely exit the application

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# 内网文件传输工具

一个简单易用的内网文件传输工具，可以在局域网内快速传输文件，支持多文件同时上传。

## 功能特点

- 通过界面进行操作，简洁直观
- 支持多文件同时上传，最大支持1GB
- 支持拖拽上传文件
- 实时显示上传进度
- 文件可以直接下载或删除（支持批量删除）
- 自动显示不同类型文件的图标
- 显示文件大小信息
- 可以打包为可执行文件，无需安装Python环境

## 系统要求

- 支持 Windows（已测试Windows 10/11）
- Python 3.8 - 3.13（已解决Python 3.13的兼容性问题）

## 依赖项

- flask==2.3.3
- flask-socketio==5.3.4
- pywebview==4.3
- simple-websocket==1.0.0
- Werkzeug==2.3.7
- pyinstaller==6.12.0

## 使用方法

### 方法一：直接运行 Python 脚本

1. 安装依赖：`pip install -r requirements.txt`
2. 运行应用：`python app.py`
3. 程序会自动打开一个窗口显示文件传输界面

### 方法二：使用可执行文件

1. 运行构建脚本：`python build_exe.py`或`build.bat`
2. 等待构建完成
3. 在 `dist/内网文件传输工具` 目录中找到可执行文件
4. 双击运行可执行文件，将打开一个窗口显示文件传输界面

## Python 3.13兼容性说明

本项目已完全兼容Python 3.13，采用threading模式运行Flask-SocketIO，并使用pywebview作为统一界面，创建独立的应用窗口。所有依赖项均已经过兼容性测试。

## 构建说明

构建可执行文件时：
- 使用PyInstaller 6.12.0打包，自动配置所需的依赖和导入项
- 采用单目录模式(--onedir)打包，生成独立的应用目录
- 自动安装requirements.txt中的所有依赖项
- 自动创建和配置uploads上传目录
- 使用threading模式运行Flask-SocketIO，避免gevent兼容性问题
- 支持Windows系统，自动获取本机IP地址
- 支持Python 3.8至3.13版本，自动检查版本兼容性
- 构建过程全自动化，无需手动配置

## 注意事项

1. 程序会在当前目录下创建 `uploads` 文件夹存储上传的文件
2. 首次运行时可能会被防火墙拦截，请允许访问
3. 如需在其他电脑上运行生成的exe文件，需要将整个 `dist/内网文件传输工具` 目录复制过去
4. 关闭窗口即可完全退出应用