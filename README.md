# 内网文件传输工具

<p align="center">
  <img src="static/app_icon.svg" alt="LAN File Transfer Tool Logo" width="150" height="150">
</p>

<div align="center">
  <!-- 项目信息 -->
  <a href="https://github.com/MagicCD/Transfer"><img src="https://img.shields.io/badge/python-3.8+-brightgreen?style=flat-square" alt="Python Version"></a>
  <a href="https://github.com/MagicCD/Transfer/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square" alt="License"></a>
  <a href="https://github.com/MagicCD/Transfer/releases/latest"><img src="https://img.shields.io/badge/release-v1.0.0-blue?style=flat-square" alt="Latest Release"></a>
  <a href="https://github.com/MagicCD/Transfer/releases"><img src="https://img.shields.io/github/downloads/MagicCD/Transfer/total?style=flat-square&color=blue&logo=github" alt="Total Downloads"></a>
  <br/>
  <a href="https://github.com/MagicCD/Transfer/actions"><img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" alt="Build Status"></a>
  <a href="https://github.com/MagicCD/Transfer/stargazers"><img src="https://img.shields.io/github/stars/MagicCD/Transfer?style=flat-square&color=yellow" alt="Stars"></a>
</div>

一个简单易用的内网文件传输工具，可在局域网内快速传输文件。这个轻量级应用程序使同一网络上的设备之间能够无缝共享文件，无需复杂设置或外部服务。

## Features

✨ **简洁界面** - 干净直观的用户界面  
📁 **多文件上传** - 一次上传多个文件（最大5GB）  
🖱️ **拖放上传** - 简单的拖放文件上传功能  
📦 **分块上传** - 大文件（>50MB）自动分块上传  
⏹️ **取消上传** - 可以停止正在进行的文件上传  
🔄 **实时更新** - 文件列表在所有连接的客户端实时更新  
🚀 **快速传输** - 通过本地网络直接传输以获得最大速度  
💻 **跨平台** - 支持Windows、macOS和Linux  

## 安装

### 环境要求

- Python 3.8 - 3.13
- Flask 2.3.3
- Flask-SocketIO 5.3.4
- PyWebView 4.3
- Werkzeug 2.3.7
- Simple-WebSocket 1.0.0

### 快速安装

1. 克隆仓库：
```bash
git clone https://github.com/MagicCD/Transfer.git
cd Transfer
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python main.py
```

## 使用方法

1. 使用 `python main.py` 启动应用
2. 应用将在窗口中打开并显示您的本地IP地址
3. 同一网络上的其他设备可以通过网络浏览器访问显示的IP地址和端口（例如 `http://192.168.1.100:5000`）
4. 通过将文件拖放到上传区域或点击"选择文件"按钮上传文件
5. 点击每个文件旁边的"下载"按钮下载文件
6. 使用"删除"按钮删除文件

## 构建说明

如果您想构建独立的可执行文件，请参考wiki中的[构建说明](https://github.com/MagicCD/Transfer/wiki/Build-Instructions)。

## 贡献

欢迎贡献！请随时提交Pull Request。

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加一些很棒的功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅[LICENSE](LICENSE)文件。

## 截图

[在此插入截图]