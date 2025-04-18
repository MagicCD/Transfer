# 配置说明

本文档详细说明了内网文件传输工具的所有配置项、验证规则和默认值。

## 配置加载顺序

配置按以下顺序加载，后加载的配置会覆盖先加载的配置：

1. Pydantic 模型默认值
2. 环境特定配置（开发环境、生产环境或测试环境）
3. 环境变量
4. 本地配置（`local_settings.py`，如果存在）

## 环境检测

应用程序会自动检测运行环境：

- 如果是打包后的可执行文件，则使用生产环境配置
- 否则，从环境变量 `FLASK_ENV` 中获取运行环境，默认为开发环境
- 可选值：`development`、`production`、`test`

## 配置项

### 应用基础配置

| 配置项 | 类型 | 默认值 | 环境变量 | 说明 | 验证规则 |
|-------|------|-------|---------|------|---------|
| `SECRET_KEY` | 字符串 | `'your-secret-key'` | `SECRET_KEY` | 应用程序密钥，用于会话加密等安全功能 | 必需项 |
| `SERVER_PORT` | 整数 | `5000` | `SERVER_PORT` | 服务器监听端口 | 必需项，范围：1024-65535 |
| `DEBUG` | 布尔值 | 开发环境：`True`<br>生产环境：`False` | `DEBUG` | 是否启用调试模式 | 可选项 |
| `SECURE_COOKIES` | 布尔值 | 开发环境：`False`<br>生产环境：`True` | `SECURE_COOKIES` | 是否启用安全Cookie | 可选项 |

### 文件上传配置

| 配置项 | 类型 | 默认值 | 环境变量 | 说明 | 验证规则 |
|-------|------|-------|---------|------|---------|
| `UPLOAD_FOLDER` | 字符串 | `'uploads'` | `UPLOAD_FOLDER` | 上传文件存储目录 | 必需项，如果目录不存在将自动创建 |
| `TEMP_CHUNKS_DIR` | 字符串 | `'uploads/.temp_chunks'` | `TEMP_CHUNKS_DIR` | 临时分块文件存储目录 | 必需项，如果目录不存在将自动创建 |
| `MAX_CONTENT_LENGTH` | 整数 | `5 * GB` (5GB) | `MAX_CONTENT_LENGTH` | 最大上传文件大小（字节） | 必需项，范围：1MB-10GB |
| `CHUNK_SIZE` | 整数 | `5 * MB` (5MB) | `CHUNK_SIZE` | 文件分块大小（字节） | 必需项，范围：1MB-100MB，必须小于或等于分块上传阈值 |
| `CHUNKED_UPLOAD_THRESHOLD` | 整数 | `50 * MB` (50MB) | `CHUNKED_UPLOAD_THRESHOLD` | 启用分块上传的文件大小阈值（字节） | 必需项，范围：1MB-1GB，必须小于或等于最大内容长度 |

### 缓存和临时文件配置

| 配置项 | 类型 | 默认值 | 环境变量 | 说明 | 验证规则 |
|-------|------|-------|---------|------|---------|
| `FILES_CACHE_TTL` | 整数 | 开发环境：`5`<br>生产环境：`30` | `FILES_CACHE_TTL` | 文件列表缓存有效期（秒） | 必需项，范围：1-3600 |
| `TEMP_FILES_MAX_AGE` | 整数 | 开发环境：`2`<br>生产环境：`24` | `TEMP_FILES_MAX_AGE` | 临时文件最长保存时间（小时） | 必需项，范围：1-168 |

### 日志配置

| 配置项 | 类型 | 默认值 | 环境变量 | 说明 | 验证规则 |
|-------|------|-------|---------|------|---------|
| `LOG_LEVEL` | 字符串 | 开发环境：`'DEBUG'`<br>生产环境：`'INFO'` | `LOG_LEVEL` | 日志级别 | 必需项，可选值：`'DEBUG'`, `'INFO'`, `'WARNING'`, `'ERROR'`, `'CRITICAL'` |
| `LOG_FORMAT` | 字符串 | `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'` | 无 | 日志格式 | 必需项 |

## 环境特定配置

### 开发环境（development）

| 配置项 | 值 |
|-------|-----|
| `DEBUG` | `True` |
| `LOG_LEVEL` | `'DEBUG'` |
| `TEMP_FILES_MAX_AGE` | `2` |
| `FILES_CACHE_TTL` | `5` |

### 生产环境（production）

| 配置项 | 值 |
|-------|-----|
| `DEBUG` | `False` |
| `LOG_LEVEL` | `'INFO'` |
| `TEMP_FILES_MAX_AGE` | `24` |
| `FILES_CACHE_TTL` | `30` |
| `SECURE_COOKIES` | `True` |

### 测试环境（test）

| 配置项 | 值 |
|-------|-----|
| `DEBUG` | `True` |
| `LOG_LEVEL` | `'DEBUG'` |
| `TEMP_FILES_MAX_AGE` | `1` |
| `FILES_CACHE_TTL` | `1` |
| `UPLOAD_FOLDER` | 临时目录 |
| `TEMP_CHUNKS_DIR` | 临时目录 |

## 本地配置

你可以创建一个 `local_settings.py` 文件来覆盖任何配置项。此文件不会被版本控制系统跟踪，适合存放本地开发环境的特定配置。

示例：

```python
# 调试模式
DEBUG = True

# 自定义密钥
SECRET_KEY = 'your-custom-dev-key'

# 自定义上传目录
UPLOAD_FOLDER = 'custom/uploads/path'

# 日志级别
LOG_LEVEL = 'DEBUG'
```

## 环境变量

你也可以通过环境变量来设置配置项。创建一个 `.env` 文件，并按照 `.env.example` 中的示例设置环境变量。

示例：

```
SECRET_KEY=your-secret-key-here
SERVER_PORT=5000
FLASK_ENV=development
UPLOAD_FOLDER=uploads
TEMP_CHUNKS_DIR=uploads/.temp_chunks
MAX_CONTENT_LENGTH=5368709120
```

## 使用 Pydantic 的好处

使用 Pydantic 进行配置管理有以下好处：

1. **类型安全**：所有配置项都有明确的类型注解，可以在运行前捕获类型错误
2. **自动验证**：配置项的值会自动根据验证规则进行验证，确保配置的正确性
3. **默认值**：可以为配置项设置默认值，简化配置过程
4. **文档化**：配置项的定义包含详细的说明，方便开发者了解配置项的用途和限制
5. **环境特定配置**：可以为不同的环境设置不同的配置值，简化环境切换
