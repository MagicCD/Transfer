# 内网文件传输工具

<p align="center">
  <img src="static/app_icon.svg" alt="文件快传" width="150" height="150">
</p>

<div align="center">
  <a href="https://github.com/MagicCD/Transfer/actions"><img src="https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square" alt="Build Status"></a>
  <a href="https://pypi.org/project/Flask/"><img src="https://img.shields.io/badge/Flask-2.3.3-blue?style=flat-square" alt="Flask Version"></a>
  <a href="https://github.com/MagicCD/Transfer/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License"></a>
  <a href="https://github.com/MagicCD/Transfer/releases"><img src="https://img.shields.io/github/downloads/MagicCD/Transfer/total?style=flat-square&color=blue" alt="Downloads"></a>
  <br/>
  <a href="https://github.com/MagicCD/Transfer/stargazers"><img src="https://img.shields.io/github/stars/MagicCD/Transfer?style=flat-square&color=yellow" alt="Stars"></a>
</div>

---

## 🚀 项目简介  
一个轻量级的局域网文件传输工具，提供直观的Web界面和强大的文件管理功能。支持大文件分块上传、实时同步、跨平台运行，适用于家庭/办公室内设备间快速文件共享。

---

## 🌟 核心功能  
| 功能分类 | 功能描述 |
|---------|----------|
| **基础功能** | ✅ 多文件上传（最大5GB）<br>✅ 拖放上传<br>✅ 实时文件列表同步 |
| **高级功能** | ✅ 大文件分块上传（>50MB）<br>✅ **暂停/恢复上传**（支持单文件/全部文件）<br>✅ 批量删除文件 |
| **系统特性** | ✅ 跨平台支持（Windows/macOS/Linux）<br>✅ **自动清理过期临时文件**（默认保留2小时）<br>✅ **智能文件图标识别**（支持20+文件类型）<br>✅ 安全的WebSocket通信 |

---

## 🛠️ 安装指南  
### 环境要求  
| 依赖库 | 版本要求 | 作用 |
|--------|----------|------|
| Python | 3.8-3.13 | 运行环境 |
| Flask | 2.3.3 | Web框架 |
| Flask-SocketIO | 5.3.4 | 实时通信 |
| PyWebView | 4.3 | 桌面窗口封装 |
| Werkzeug | 2.3.7 | 请求处理 |

### 快速安装  
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

---

## 📱 使用示例  
![alt text](static/screenshot.png)  
1. 运行后自动打开桌面窗口，显示本地IP地址（如 `http://192.168.1.100:5000`）  
2. **上传文件**：拖拽文件到上传区域或点击"选择文件"  
3. **管理文件**：  
   - 点击文件旁的"下载"按钮下载  
   - 点击"删除"按钮移除单个文件  
   - 点击顶部"清空全部"删除所有文件  
4. **大文件上传**：  
   - 自动分块上传（>50MB）  
   - 点击文件旁的"暂停/恢复"按钮控制单个文件进度  
   - 点击顶部按钮控制全部文件上传状态  

---

## 📦 构建可执行文件  
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

---

## 🛠️ 开发贡献  
1. **Fork仓库**并创建功能分支  
   ```bash
   git checkout -b feature/your-feature
   ```  
2. **代码规范**  
   - 遵循PEP8规范  
   - 单元测试覆盖率需≥80%  
3. **提交PR前**  
   - 确保通过所有CI检查  
   - 添加测试用例（修改核心逻辑时）  
   - 更新文档说明  

---

## 🆘 常见问题  
**Q: 服务器启动失败？**  
A: 检查：  
- 端口5000未被占用  
- 依赖库版本是否匹配  
- 防火墙设置  

**Q: 文件上传后无法下载？**  
A: 确认：  
- 文件存储路径权限（默认`uploads/`）  
- 浏览器缓存清除  
- 服务端日志排查  

---

## 📚 文档
详细的文档可在 `docs/` 目录中找到，包括中文和英文版本。

### 中文文档

- [安装指南](docs/zh_CN/setup.md) - 详细的安装和部署说明
- [配置说明](docs/zh_CN/configuration.md) - 所有配置项、验证规则和默认值
- [API文档](docs/zh_CN/api.md) - 所有API接口的详细说明
- [常见问题](docs/zh_CN/faq.md) - 常见问题和解决方案
- [贡献指南](docs/zh_CN/contribution.md) - 如何参与项目开发

### English Documentation

- [Installation Guide](docs/en/setup.md) - Detailed installation and deployment instructions
- [Configuration Guide](docs/en/configuration.md) - All configuration options, validation rules, and default values
- [API Documentation](docs/en/api.md) - Detailed description of all API endpoints
- [Frequently Asked Questions](docs/en/faq.md) - Common questions and solutions
- [Contribution Guidelines](docs/en/contribution.md) - How to participate in project development

## 📄 许可证  
MIT License - 详情见[LICENSE](LICENSE)文件  
```  
允许：  
✓ 商业使用  
✓ 修改和分发  
✓ 私有部署  

禁止：  
✗ 移除版权声明  
✗ 追究代码问题责任  
```  

---

## 📢 联系我  
- GitHub仓库：[https://github.com/MagicCD/Transfer](https://github.com/MagicCD/Transfer)  
- CSDN博客：[https://blog.csdn.net/qq_52357217](https://blog.csdn.net/qq_52357217)
