# Installation Guide

This document provides detailed installation and deployment instructions for the LAN File Transfer Tool.

## System Requirements

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.8-3.13 | Runtime environment |
| Flask | 2.3.3 | Web framework |
| Flask-SocketIO | 5.3.4 | Real-time communication |
| PyWebView | 4.3 | Desktop window wrapper |
| Werkzeug | 2.3.7 | Request handling |

## Quick Installation

### From Source Code

```bash
# Clone the repository
git clone https://github.com/MagicCD/Transfer.git
cd Transfer

# Install dependencies (virtual environment recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

# Start the application
python app.py
```

### Using Executable File

1. Download the latest executable file from the [Releases](https://github.com/MagicCD/Transfer/releases) page
2. Double-click to run, no need to install Python or other dependencies

## Building Executable File

If you want to build the executable file yourself, follow these steps:

```bash
# Install packaging tool
pip install pyinstaller

# Packaging command (Windows/Linux)
pyinstaller --onefile --windowed \
--add-data "templates;templates" \
--add-data "static;static" \
--icon=static/app_icon.ico \
main.py

# macOS specific parameters (requires different path separator)
pyinstaller --onefile --windowed \
--add-data "templates:templates" \
--add-data "static:static" \
--icon=static/app_icon.icns \
main.py
```

After building, the executable file will be located in the `dist` directory.

## Network Configuration

By default, the application listens on port 5000 on all network interfaces. If you need to change the port or limit the listening network interface, you can configure it in the following ways:

1. Set the `SERVER_PORT` environment variable in the `.env` file
2. Or specify it via command line arguments when starting the application: `python app.py --port 8080`

## Firewall Settings

If you are using this tool in a LAN, you may need to allow the port used by the application in your firewall:

- Windows: Add an exception rule in "Windows Firewall"
- macOS: Add an exception in "System Preferences > Security & Privacy > Firewall"
- Linux: Add a rule using `ufw` or other firewall tools, for example: `sudo ufw allow 5000/tcp`

## Common Issues

### Port in Use

If you get a "port in use" error when starting, try these solutions:

1. Change the port: Set `SERVER_PORT=another_port_number` in the `.env` file
2. Close the application that is using the port
3. Use `netstat -ano | findstr 5000` (Windows) or `lsof -i :5000` (macOS/Linux) to find the process using the port

### Dependency Installation Failure

If you encounter issues installing dependencies, try:

1. Update pip: `pip install --upgrade pip`
2. Use a mirror repository: `pip install -r requirements.txt -i https://pypi.org/simple`
3. Install problematic dependencies individually to see detailed error messages

### File Upload Failure

If file uploads fail, check:

1. Whether the file size exceeds the limit (default 5GB)
2. Whether the upload directory has write permissions
3. Whether there is sufficient disk space

## Further Help

If you encounter other issues, please check the [FAQ](./faq.md) document or ask questions in [GitHub Issues](https://github.com/MagicCD/Transfer/issues).
