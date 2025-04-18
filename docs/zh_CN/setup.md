# 安装指南

本文档提供了内网文件传输工具的详细安装和部署说明。

## 环境要求

| 依赖库 | 版本要求 | 作用 |
|--------|----------|------|
| Python | 3.8-3.13 | 运行环境 |
| Flask | 2.3.3 | Web框架 |
| Flask-SocketIO | 5.3.4 | 实时通信 |
| PyWebView | 4.3 | 桌面窗口封装 |
| Werkzeug | 2.3.7 | 请求处理 |

## 快速安装

### 从源代码安装

```bash
# 克隆仓库
git clone https://github.com/MagicCD/Transfer.git
cd Transfer

# 安装依赖（推荐使用虚拟环境）
python -m venv venv
source venv/bin/activate  # Windows用 `venv\Scripts\activate`
pip install -r requirements.txt

# 启动应用
python app.py
```

### 使用可执行文件

1. 从 [Releases](https://github.com/MagicCD/Transfer/releases) 页面下载最新版本的可执行文件
2. 双击运行即可，无需安装Python或其他依赖

## 构建可执行文件

如果您想自己构建可执行文件，可以按照以下步骤操作：

```bash
# 安装打包工具
pip install pyinstaller

# 打包命令（Windows/Linux）
pyinstaller --onefile --windowed \
--add-data "templates;templates" \
--add-data "static;static" \
--icon=static/app_icon.ico \
main.py

# macOS特殊参数（需指定路径分隔符）
pyinstaller --onefile --windowed \
--add-data "templates:templates" \
--add-data "static:static" \
--icon=static/app_icon.icns \
main.py
```

构建完成后，可执行文件将位于 `dist` 目录中。

## 网络配置

默认情况下，应用会监听所有网络接口的 5000 端口。如果您需要更改端口或限制监听的网络接口，可以通过以下方式配置：

1. 在 `.env` 文件中设置 `SERVER_PORT` 环境变量
2. 或者在启动应用时通过命令行参数指定：`python app.py --port 8080`

## 防火墙设置

如果您在局域网中使用此工具，可能需要在防火墙中允许应用使用的端口：

- Windows: 在"Windows防火墙"中添加例外规则
- macOS: 在"系统偏好设置 > 安全性与隐私 > 防火墙"中添加例外
- Linux: 使用 `ufw` 或其他防火墙工具添加规则，例如：`sudo ufw allow 5000/tcp`

## 常见问题

### 端口被占用

如果启动时提示端口被占用，可以尝试以下解决方案：

1. 更改端口：在 `.env` 文件中设置 `SERVER_PORT=其他端口号`
2. 关闭占用端口的应用
3. 使用 `netstat -ano | findstr 5000` (Windows) 或 `lsof -i :5000` (macOS/Linux) 查找占用端口的进程

### 依赖库安装失败

如果安装依赖库时遇到问题，可以尝试：

1. 更新 pip: `pip install --upgrade pip`
2. 使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
3. 单独安装有问题的依赖库，查看详细错误信息

### 文件上传失败

如果文件上传失败，请检查：

1. 文件大小是否超过限制（默认5GB）
2. 上传目录是否有写入权限
3. 磁盘空间是否充足

## 更多帮助

如果您遇到其他问题，请查看[常见问题](./faq.md)文档或在 [GitHub Issues](https://github.com/MagicCD/Transfer/issues) 中提问。
