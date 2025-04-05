<p align="center">
  <img src="static/app_icon.svg" alt="LAN File Transfer Tool Logo" width="150" height="150">
</p>

<h1 align="center">LAN File Transfer Tool</h1>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.13-blue" alt="Python Version"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-2.3.3-red" alt="Flask"></a>
  <a href="https://socketio.io/"><img src="https://img.shields.io/badge/SocketIO-5.3.4-green" alt="SocketIO"></a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#build">Build</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#faq">FAQ</a> •
  <a href="#license">License</a> •
  <a href="#内网文件传输工具">中文文档</a>
</p>

A simple and easy-to-use LAN file transfer tool that allows quick file transfers within a local network. This lightweight application enables seamless file sharing between devices on the same network without the need for complex setup or external services.

## Features

✨ **Simple Interface** - Clean and intuitive user interface  
📁 **Multiple File Uploads** - Upload multiple files at once (up to 1GB)  
🖱️ **Drag and Drop** - Easy drag and drop file upload functionality  
📊 **Real-time Progress** - See upload progress in real-time  
⬇️ **Direct Downloads** - One-click downloads of shared files  
🗑️ **File Management** - Delete individual files or all files at once  
🔍 **File Type Icons** - Visual identification of different file types  
📏 **Size Information** - Display of file sizes in appropriate units  
📦 **Standalone Application** - Can be packaged as an executable file  
🌐 **No Internet Required** - Works completely offline within your LAN  

## Installation

### Prerequisites

- Windows (tested on Windows 10/11)
- Python 3.8 - 3.13

### Method 1: From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/lan-file-transfer.git
cd lan-file-transfer

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Method 2: Executable File

1. Download the latest release from the [Releases](https://github.com/yourusername/lan-file-transfer/releases) page
2. Extract the zip file
3. Run `内网文件传输工具.exe`

## Usage

1. Launch the application
2. The tool will automatically open in a window showing your local IP address
3. Other devices on the same network can access the tool by navigating to the shown address in their browser
4. Select files to upload by clicking "选择文件" or by dragging and dropping files onto the upload area
5. Click "上传文件" to start the upload
6. Files can be downloaded or deleted by any device connected to the tool

## Build

To build the executable yourself:

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Run the build script
python build_exe.py
# or
build.bat
```

The executable will be created in the `dist/内网文件传输工具` directory.

## Screenshots

[Add screenshots here]

## FAQ

### Q: Is my data secure?
**A:** The tool operates only within your local network. No data is sent to external servers.

### Q: What's the file size limit?
**A:** The default limit is 1GB per file, but this can be modified in the code.

### Q: Can I use this on platforms other than Windows?
**A:** The Python script will run on any platform with Python 3.8+, but the executable is Windows-only.

### Q: Does this work over the internet?
**A:** No, this tool is designed for local network use only for security reasons.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# 内网文件传输工具

<p align="center">
  <a href="#功能特点">功能特点</a> •
  <a href="#安装方法">安装方法</a> •
  <a href="#使用方法">使用方法</a> •
  <a href="#构建方法">构建方法</a> •
  <a href="#常见问题">常见问题</a> •
  <a href="#贡献">贡献</a> •
  <a href="#许可证">许可证</a>
</p>

一个简单易用的内网文件传输工具，可以在局域网内快速传输文件。这个轻量级应用程序可以让同一网络上的设备之间无需复杂设置或外部服务即可无缝共享文件。

## 功能特点

✨ **简洁界面** - 清晰直观的用户界面  
📁 **多文件上传** - 一次上传多个文件（最大支持1GB）  
🖱️ **拖拽上传** - 轻松拖拽文件上传功能  
📊 **实时进度** - 实时查看上传进度  
⬇️ **直接下载** - 一键下载共享文件  
🗑️ **文件管理** - 删除单个文件或一次性删除所有文件  
🔍 **文件类型图标** - 不同文件类型的视觉识别  
📏 **大小信息** - 以适当单位显示文件大小  
📦 **独立应用程序** - 可打包为可执行文件  
🌐 **无需互联网** - 在局域网内完全离线工作  

## 安装方法

### 环境要求

- Windows（已在Windows 10/11上测试）
- Python 3.8 - 3.13

### 方法一：从源代码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/lan-file-transfer.git
cd lan-file-transfer

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

### 方法二：使用可执行文件

1. 从[发布页面](https://github.com/yourusername/lan-file-transfer/releases)下载最新版本
2. 解压缩文件
3. 运行`内网文件传输工具.exe`

## 使用方法

1. 启动应用程序
2. 工具将自动在窗口中显示您的本地IP地址
3. 同一网络上的其他设备可以通过在浏览器中导航到显示的地址来访问该工具
4. 通过点击"选择文件"或将文件拖放到上传区域来选择要上传的文件
5. 点击"上传文件"开始上传
6. 任何连接到该工具的设备都可以下载或删除文件

## 构建方法

要自行构建可执行文件：

```bash
# 如果尚未安装PyInstaller，请先安装
pip install pyinstaller

# 运行构建脚本
python build_exe.py
# 或者
build.bat
```

可执行文件将在`dist/内网文件传输工具`目录中创建。

## 常见问题

### 问：我的数据安全吗？
**答：**该工具仅在您的本地网络内运行。不会将数据发送到外部服务器。

### 问：文件大小限制是多少？
**答：**默认限制为每个文件1GB，但可以在代码中修改此限制。

### 问：我可以在Windows以外的平台上使用此工具吗？
**答：**Python脚本可以在任何安装了Python 3.8+的平台上运行，但可执行文件仅适用于Windows。

### 问：这个工具可以通过互联网工作吗？
**答：**不可以，出于安全考虑，此工具仅设计用于本地网络使用。

## 贡献

欢迎贡献！提交拉取请求前请阅读我们的[贡献指南](CONTRIBUTING.md)。

## 许可证

本项目采用MIT许可证 - 有关详细信息，请参阅[LICENSE](LICENSE)文件。