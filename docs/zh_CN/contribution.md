# 贡献指南

感谢您考虑为内网文件传输工具做出贡献！本文档提供了参与项目开发的详细指南。

## 贡献流程

### 1. 准备工作

1. 在GitHub上Fork项目仓库
2. 将Fork后的仓库克隆到本地
   ```bash
   git clone https://github.com/YOUR_USERNAME/Transfer.git
   cd Transfer
   ```
3. 添加上游仓库
   ```bash
   git remote add upstream https://github.com/MagicCD/Transfer.git
   ```
4. 创建新的分支
   ```bash
   git checkout -b feature/your-feature-name
   ```

### 2. 开发环境设置

1. 创建并激活虚拟环境
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows用 `venv\Scripts\activate`
   ```
2. 安装依赖
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   ```
3. 安装pre-commit钩子
   ```bash
   pre-commit install
   ```

### 3. 开发规范

#### 代码风格

- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)代码风格指南
- 使用4个空格进行缩进，不使用制表符
- 行长度不超过100个字符
- 使用有意义的变量名和函数名
- 添加适当的注释和文档字符串

#### 提交规范

- 提交消息应简洁明了，描述本次提交的主要内容
- 使用现在时态（"Add feature"而不是"Added feature"）
- 第一行是标题，不超过50个字符
- 如果需要详细说明，在标题后空一行，然后添加详细描述

示例：
```
Add chunked upload progress tracking

- Add real-time progress tracking for chunked uploads
- Implement WebSocket events for progress updates
- Update UI to display progress bar for each chunk
```

### 4. 测试

- 为新功能或修复的bug编写测试
- 确保所有测试都能通过
- 测试覆盖率应达到80%以上

运行测试：
```bash
pytest
```

检查测试覆盖率：
```bash
pytest --cov=app
```

### 5. 提交变更

1. 将您的更改添加到暂存区
   ```bash
   git add .
   ```
2. 提交更改
   ```bash
   git commit -m "Your commit message"
   ```
3. 将本地分支推送到您的Fork仓库
   ```bash
   git push origin feature/your-feature-name
   ```
4. 在GitHub上创建Pull Request

### 6. 代码审查

- 耐心等待代码审查
- 根据审查意见进行修改
- 如果需要更新Pull Request，只需将更改推送到相同的分支

## 项目结构

了解项目结构有助于您更好地贡献代码：

```
app/
├── api/                  # API层
│   ├── v1/             # API版本控制
│   └── middlewares/    # 中间件
├── core/                 # 核心功能模块
│   ├── exceptions/      # 统一异常处理
│   ├── interfaces/      # 抽象接口定义
│   └── validators/      # 数据验证器
├── services/             # 服务层
│   ├── file/            # 文件服务
│   ├── upload/          # 上传服务
│   └── cache/           # 缓存服务
├── utils/                # 工具函数
└── config/               # 配置管理
    └── models.py        # 配置模型

static/                   # 静态资源
templates/                # HTML模板
tests/                    # 测试代码
docs/                     # 文档
```

## 功能开发指南

### 添加新API

1. 在 `app/api/v1/` 目录下创建新的模块或在现有模块中添加新的路由
2. 遵循RESTful API设计原则
3. 使用 `api_error_handler` 装饰器处理异常
4. 更新API文档

### 修改前端界面

1. 前端代码位于 `static/js/` 和 `templates/` 目录
2. 遵循现有的代码风格和组织结构
3. 确保兼容主流浏览器
4. 测试不同设备和屏幕尺寸的显示效果

### 添加新配置项

1. 在 `app/config/models.py` 中的适当配置模型中添加新配置项
2. 添加适当的类型注解和验证规则
3. 提供合理的默认值
4. 更新配置文档

## 文档贡献

文档位于 `docs/` 目录，分为中文和英文两个版本。如果您修改了功能或添加了新功能，请同时更新相应的文档。

## 报告Bug

如果您发现了Bug但没有时间修复，请在GitHub上提交Issue，包括：

1. Bug的详细描述
2. 重现步骤
3. 预期行为和实际行为
4. 您的环境信息（操作系统、Python版本等）
5. 相关的日志或错误消息

## 提出功能建议

如果您有新功能的想法，请在GitHub上提交Issue，描述：

1. 您想要的功能
2. 为什么这个功能对项目有价值
3. 如何实现（如果您有想法）

## 行为准则

请遵循项目的行为准则，保持尊重和专业。我们欢迎所有人的贡献，不分背景和经验水平。

## 许可证

通过贡献代码，您同意您的贡献将在MIT许可证下获得许可。
