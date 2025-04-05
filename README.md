# LAN File Transfer Tool

<p align="center">
  <img src="static/app_icon.svg" alt="LAN File Transfer Tool Logo" width="150" height="150">
</p>

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