<p align="center">
  <img src="static/app_icon.svg" alt="LAN File Transfer Tool Logo" width="150" height="150">
</p>

<h1 align="center">LAN File Transfer Tool</h1>

<!-- AI GENERATED SECTION -->
<p align="center">
  <a href="#version-history">Version 1.2.0</a>
</p>

<div align="center">

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.2.0** | 2025-04-05 | • ✨ **改进项目结构** <br>• ✅ 添加待上传文件删除功能 <br>• 🎨 美化UI和文档 |
| **1.1.1** | 2025-04-05 | • 🎨 重新设计图标，使用更轻量级的线条和柔和的色调 <br>• 避免大面积深色 |
| **1.1.0** | 2025-04-05 | • 🎨 更新图标设计，使其更直观地表达局域网文件传输功能 <br>• 📝 在README中添加图标说明 |

</div>
<!-- AI GENERATED SECTION -->

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.13-blue" alt="Python Version"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-2.3.3-red" alt="Flask"></a>
  <a href="https://flask-socketio.readthedocs.io/"><img src="https://img.shields.io/badge/Flask--SocketIO-5.3.4-green" alt="Flask-SocketIO"></a>
  <a href="https://pywebview.flowrl.com/"><img src="https://img.shields.io/badge/PyWebView-4.3-purple" alt="PyWebView"></a>
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

### Dependencies

```
flask==2.3.3
flask-socketio==5.3.4
pywebview==4.3
simple-websocket==1.0.0
Werkzeug==2.3.7
pyinstaller==6.12.0
```

### Method 1: From Source

```bash
# Clone the repository
git clone https://github.com/MagicCD/Transfer.git
cd Transfer

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Method 2: Executable File

1. Download the latest release from the [Releases](https://github.com/MagicCD/Transfer/releases) page
2. Extract the zip file
3. Run `内网文件传输工具.exe`

## Usage

1. Launch the application
2. The tool will automatically open in a window showing your local IP address
3. Other devices on the same network can access the tool by navigating to the shown address in their browser
4. Select files to upload by clicking "选择文件" or by dragging and dropping files onto the upload area
5. Click "上传文件" to start the upload
6. Files can be downloaded or deleted by any device connected to the tool

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

When you run the application:
1. A web server starts on port 5000
2. A PyWebView window opens displaying the web interface
3. The application automatically detects your local IP address
4. Other devices on the same network can access via http://YOUR_IP:5000

## API Documentation

The application exposes the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main interface for file transfers |
| `/upload` | POST | Upload files (accepts multipart/form-data) |
| `/download/<filename>` | GET | Download a specific file |
| `/delete/<filename>` | DELETE | Delete a specific file |
| `/delete_all` | DELETE | Delete all files |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client → Server | Client connection event |
| `files_updated` | Server → Client | Notifies clients when files are changed |
| `upload_progress` | Client → Server | Reports upload progress |
| `upload_progress_update` | Server → Client | Broadcasts upload progress to all clients |

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

<!-- AI GENERATED SECTION -->
## Documentation

This project uses automated documentation processes:

- **Version History**: Automatically generated from Git commit history
- **API Documentation**: Generated from code analysis
- **Wiki Synchronization**: The GitHub Wiki is automatically updated when README.md changes
- **Project Structure**: Generated using the `tree` command

All documentation follows [Markdown lint rules](https://github.com/DavidAnson/markdownlint) (MD025/MD040 etc.) to ensure consistency.
<!-- AI GENERATED SECTION -->

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.