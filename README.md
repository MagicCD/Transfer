# 内网文件传输工具

一个简单高效的内网文件传输工具，基于Flask、Flask-SocketIO和PyWebView构建。可以在局域网内快速共享和传输文件，无需复杂配置。

## 功能特点

- 简洁直观的用户界面
- 拖放式文件上传
- 实时文件列表更新
- 支持大文件传输（最大1GB）
- 支持多种文件类型，带有直观的图标显示
- 跨平台支持 (Windows, macOS, Linux)
- 适合局域网内快速文件分享

## 安装方法

### 从源代码运行

1. 克隆仓库
```bash
git clone https://github.com/yourusername/internal-file-transfer.git
cd internal-file-transfer
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
python main.py
```

### 从发布版本安装

1. 从 [Releases](https://github.com/yourusername/internal-file-transfer/releases) 页面下载最新版本
2. 直接运行可执行文件

## 使用方法

1. 启动应用后，会自动打开一个WebView窗口
2. 应用会自动获取本机IP地址，并在界面上显示
3. 其他设备可以通过浏览器访问`http://<主机IP>:5000`来连接
4. 通过拖放或点击上传区域来上传文件
5. 点击文件名即可下载文件
6. 点击删除按钮可删除单个文件或清空所有文件

## 技术栈

- 后端: Python, Flask, Flask-SocketIO
- 前端: HTML, CSS, JavaScript, Bootstrap 5
- 界面: PyWebView

## 要求

- Python 3.8 或更高版本
- 依赖项 (详见 requirements.txt)
  - flask==2.3.3
  - flask-socketio==5.3.4
  - pywebview==4.3
  - simple-websocket==1.0.0 

## 打包说明

如需将应用打包为单个可执行文件，可使用提供的build.py脚本：

```bash
python build.py
```

生成的可执行文件将位于`dist`目录中。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献代码或提交问题！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解更多信息。 