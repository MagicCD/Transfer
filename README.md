# LAN File Transfer Tool

<p align="center">
  <img src="static/app_icon.svg" alt="LAN File Transfer Tool Logo" width="150" height="150">
</p>

<div align="center">
  <a href="https://github.com/MagicCD/Transfer"><img src="https://img.shields.io/badge/python-3.8+-brightgreen?style=flat-square" alt="Python Version"></a>
  <a href="https://github.com/MagicCD/Transfer/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square" alt="License"></a>
  <a href="https://github.com/MagicCD/Transfer/actions"><img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" alt="Build Status"></a>
  <a href="https://github.com/MagicCD/Transfer/releases/latest"><img src="https://img.shields.io/badge/release-v1.0.0-blue?style=flat-square" alt="Latest Release"></a>
  <a href="https://github.com/MagicCD/Transfer/blob/main/README_CN.md"><img src="https://img.shields.io/badge/localized-100%25-brightgreen?style=flat-square" alt="Localization"></a>
  <br>
  <a href="https://github.com/MagicCD/Transfer/discussions"><img src="https://img.shields.io/badge/discussions-active-lightgrey?style=flat-square" alt="Discussions"></a>
  <a href="https://gitter.im/MagicCD/Transfer"><img src="https://img.shields.io/badge/chat-online-blue?style=flat-square" alt="Chat"></a>
  <a href="https://github.com/MagicCD/Transfer/releases"><img src="https://img.shields.io/badge/downloads-available-blue?style=flat-square&logo=github" alt="Downloads"></a>
  <a href="https://github.com/MagicCD/Transfer/pulls"><img src="https://img.shields.io/badge/PRs-welcome-blue?style=flat-square&logo=github" alt="GitHub Pull Requests"></a>
  <a href="https://github.com/sponsors/MagicCD"><img src="https://img.shields.io/badge/$-sponsor-ff69b4?style=flat-square" alt="Sponsor"></a>
</div>

A simple and easy-to-use LAN file transfer tool that allows quick file transfers within a local network. This lightweight application enables seamless file sharing between devices on the same network without the need for complex setup or external services.

## Features

✨ **Simple Interface** - Clean and intuitive user interface  
📁 **Multiple File Uploads** - Upload multiple files at once (up to 1GB)  
🖱️ **Drag and Drop** - Easy drag and drop file upload functionality  
🔄 **Real-time Updates** - File list updates in real-time across all connected clients  
🚀 **Fast Transfers** - Direct transfers over your local network for maximum speed  
💻 **Cross-Platform** - Works on Windows, macOS and Linux  

## Installation

### Prerequisites

- Python 3.8 - 3.13
- Flask 2.3.3
- Flask-SocketIO 5.3.4
- PyWebView 4.3
- Werkzeug 2.3.7
- Simple-WebSocket 1.0.0

### Quick Install

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lan-file-transfer.git
cd lan-file-transfer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

1. Start the application using `python main.py`
2. The application will open in a window and display your local IP address
3. Other devices on the same network can access the interface through a web browser by visiting the displayed IP address and port (e.g., `http://192.168.1.100:5000`)
4. Upload files by dragging and dropping them into the upload area or by clicking the "Select Files" button
5. Download files by clicking the "Download" button next to each file
6. Delete files using the "Delete" button

## Build Instructions

If you want to build a standalone executable, please refer to the [Build Instructions](https://github.com/yourusername/lan-file-transfer/wiki/Build-Instructions) in the wiki.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Screenshots

[Insert screenshots here] 