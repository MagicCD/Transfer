# API 文档

本文档详细说明了内网文件传输工具提供的所有API接口。

## API 概览

内网文件传输工具提供了以下API接口：

| 接口类别 | 描述 |
|---------|------|
| 文件管理 | 用于获取、下载和删除文件 |
| 文件上传 | 用于上传文件，包括普通上传和分块上传 |
| 上传控制 | 用于暂停、恢复和取消上传 |

所有API都返回JSON格式的响应，包含 `success` 字段表示操作是否成功。

## 基础URL

所有API都以 `/api/v1` 为前缀。为了向后兼容，也支持不带前缀的旧版API路径。

## 文件管理API

### 获取文件列表

获取所有已上传文件的信息。

**请求**:
- 方法: `GET`
- 路径: `/api/v1/files`
- 参数:
  - `force_refresh`: 可选，布尔值，是否强制刷新缓存，默认为 `false`

**响应**:
```json
{
  "success": true,
  "files": [
    {
      "name": "example.txt",
      "size": 1024,
      "size_human": "1.0 KB",
      "type": "text/plain",
      "icon": "file-text",
      "upload_time": "2023-06-15T10:30:45",
      "upload_time_human": "2023年6月15日 10:30"
    }
  ],
  "cache_time": 1623744645.123,
  "current_time": 1623744650.456,
  "cache_ttl": 5
}
```

### 下载文件

下载指定的文件。

**请求**:
- 方法: `GET`
- 路径: `/api/v1/files/{filename}`

**响应**:
- 成功: 文件内容（二进制）
- 失败: JSON对象
  ```json
  {
    "success": false,
    "error": "文件不存在: example.txt"
  }
  ```

### 删除文件

删除指定的文件。

**请求**:
- 方法: `DELETE`
- 路径: `/api/v1/files/{filename}`

**响应**:
```json
{
  "success": true
}
```

### 删除所有文件

删除所有已上传的文件。

**请求**:
- 方法: `DELETE`
- 路径: `/api/v1/files`

**响应**:
```json
{
  "success": true,
  "deleted_count": 5
}
```

## 文件上传API

### 普通上传

上传单个文件（适用于小于50MB的文件）。

**请求**:
- 方法: `POST`
- 路径: `/api/v1/upload`
- 内容类型: `multipart/form-data`
- 参数:
  - `file`: 文件数据

**响应**:
- 成功:
  ```json
  {
    "success": true,
    "filename": "example.txt"
  }
  ```
- 文件过大:
  ```json
  {
    "success": false,
    "error": "Large file detected",
    "use_chunked_upload": true,
    "file_size": 52428800,
    "message": "此文件大小超过50MB，需要使用分块上传"
  }
  ```

### 分块上传

上传文件的一个分块（适用于大于50MB的文件）。

**请求**:
- 方法: `POST`
- 路径: `/api/v1/upload/chunk`
- 内容类型: `multipart/form-data`
- 参数:
  - `file`: 分块数据
  - `filename`: 文件名
  - `chunk_number`: 分块编号（从0开始）
  - `total_chunks`: 总分块数

**响应**:
- 成功（分块上传）:
  ```json
  {
    "success": true,
    "filename": "example.txt",
    "status": "chunk_uploaded"
  }
  ```
- 成功（所有分块上传完成）:
  ```json
  {
    "success": true,
    "filename": "example.txt",
    "status": "completed"
  }
  ```
- 上传暂停:
  ```json
  {
    "success": false,
    "error": "Upload paused",
    "paused": true
  }
  ```
- 合并失败:
  ```json
  {
    "success": false,
    "error": "Failed to merge chunks",
    "merge_failed": true,
    "missing_chunks": [3, 5, 7]
  }
  ```

## 上传控制API

### 取消上传

取消文件上传并清理临时文件。

**请求**:
- 方法: `POST`
- 路径: `/api/v1/upload/{filename}/cancel`

**响应**:
```json
{
  "success": true,
  "message": "已取消上传并清理临时文件: example.txt",
  "cleaned": true
}
```

### 暂停上传

暂停文件上传。

**请求**:
- 方法: `POST`
- 路径: `/api/v1/upload/{filename}/pause`
- 内容类型: `application/json`
- 参数:
  ```json
  {
    "chunk_index": 5
  }
  ```

**响应**:
```json
{
  "success": true,
  "message": "已暂停上传: example.txt"
}
```

### 恢复上传

恢复已暂停的文件上传。

**请求**:
- 方法: `POST`
- 路径: `/api/v1/upload/{filename}/resume`

**响应**:
```json
{
  "success": true,
  "message": "已恢复上传: example.txt",
  "last_chunk": 5,
  "has_temp_dir": true,
  "cleaned_chunks": 0
}
```

### 获取上传状态

获取文件的上传状态。

**请求**:
- 方法: `GET`
- 路径: `/api/v1/upload/{filename}/state`

**响应**:
```json
{
  "filename": "example.txt",
  "status": "uploading",
  "total_chunks": 10,
  "uploaded_chunks": 5,
  "progress": 50,
  "paused": false,
  "has_temp_dir": true
}
```

## WebSocket 事件

除了REST API外，应用还提供了WebSocket事件用于实时通信。

### 客户端事件

客户端可以发送以下事件：

| 事件名称 | 描述 | 数据格式 |
|---------|------|---------|
| `connect` | 连接到WebSocket服务器 | 无 |
| `upload_progress` | 更新上传进度 | `{"filename": "example.txt", "progress": 50}` |

### 服务器事件

服务器会发送以下事件：

| 事件名称 | 描述 | 数据格式 |
|---------|------|---------|
| `files_updated` | 文件列表已更新 | `{"files": [...]}` |
| `upload_progress_update` | 上传进度已更新 | `{"filename": "example.txt", "progress": 50}` |
| `upload_state_updated` | 上传状态已更新 | `{"filename": "example.txt", "status": "paused", "paused": true}` |

## 错误处理

所有API在发生错误时都会返回一个包含 `success: false` 和 `error` 字段的JSON对象。

常见的错误响应：

```json
{
  "success": false,
  "error": "文件不存在: example.txt"
}
```

在开发模式下，错误响应还会包含详细的错误信息和堆栈跟踪：

```json
{
  "success": false,
  "error": "文件不存在: example.txt",
  "traceback": "..."
}
```

## 状态码

API使用以下HTTP状态码：

| 状态码 | 描述 |
|-------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 请求的资源不存在 |
| 405 | 不支持的请求方法 |
| 413 | 请求实体过大 |
| 500 | 服务器内部错误 |
