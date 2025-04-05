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
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
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