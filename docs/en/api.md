# API Documentation

This document details all API endpoints provided by the LAN File Transfer Tool.

## API Overview

The LAN File Transfer Tool provides the following API endpoints:

| API Category | Description |
|--------------|-------------|
| File Management | For retrieving, downloading, and deleting files |
| File Upload | For uploading files, including regular and chunked uploads |
| Upload Control | For pausing, resuming, and canceling uploads |

All APIs return responses in JSON format, containing a `success` field indicating whether the operation was successful.

## Base URL

All APIs are prefixed with `/api/v1`. For backward compatibility, old API paths without the prefix are also supported.

## File Management API

### Get File List

Get information about all uploaded files.

**Request**:
- Method: `GET`
- Path: `/api/v1/files`
- Parameters:
  - `force_refresh`: Optional, boolean, whether to force refresh the cache, default is `false`

**Response**:
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
      "upload_time_human": "June 15, 2023 10:30"
    }
  ],
  "cache_time": 1623744645.123,
  "current_time": 1623744650.456,
  "cache_ttl": 5
}
```

### Download File

Download a specific file.

**Request**:
- Method: `GET`
- Path: `/api/v1/files/{filename}`

**Response**:
- Success: File content (binary)
- Failure: JSON object
  ```json
  {
    "success": false,
    "error": "File not found: example.txt"
  }
  ```

### Delete File

Delete a specific file.

**Request**:
- Method: `DELETE`
- Path: `/api/v1/files/{filename}`

**Response**:
```json
{
  "success": true
}
```

### Delete All Files

Delete all uploaded files.

**Request**:
- Method: `DELETE`
- Path: `/api/v1/files`

**Response**:
```json
{
  "success": true,
  "deleted_count": 5
}
```

## File Upload API

### Regular Upload

Upload a single file (suitable for files smaller than 50MB).

**Request**:
- Method: `POST`
- Path: `/api/v1/upload`
- Content Type: `multipart/form-data`
- Parameters:
  - `file`: File data

**Response**:
- Success:
  ```json
  {
    "success": true,
    "filename": "example.txt"
  }
  ```
- File too large:
  ```json
  {
    "success": false,
    "error": "Large file detected",
    "use_chunked_upload": true,
    "file_size": 52428800,
    "message": "This file is larger than 50MB and requires chunked upload"
  }
  ```

### Chunked Upload

Upload a chunk of a file (suitable for files larger than 50MB).

**Request**:
- Method: `POST`
- Path: `/api/v1/upload/chunk`
- Content Type: `multipart/form-data`
- Parameters:
  - `file`: Chunk data
  - `filename`: File name
  - `chunk_number`: Chunk number (starting from 0)
  - `total_chunks`: Total number of chunks

**Response**:
- Success (chunk uploaded):
  ```json
  {
    "success": true,
    "filename": "example.txt",
    "status": "chunk_uploaded"
  }
  ```
- Success (all chunks uploaded):
  ```json
  {
    "success": true,
    "filename": "example.txt",
    "status": "completed"
  }
  ```
- Upload paused:
  ```json
  {
    "success": false,
    "error": "Upload paused",
    "paused": true
  }
  ```
- Merge failed:
  ```json
  {
    "success": false,
    "error": "Failed to merge chunks",
    "merge_failed": true,
    "missing_chunks": [3, 5, 7]
  }
  ```

## Upload Control API

### Cancel Upload

Cancel file upload and clean up temporary files.

**Request**:
- Method: `POST`
- Path: `/api/v1/upload/{filename}/cancel`

**Response**:
```json
{
  "success": true,
  "message": "Upload cancelled and temporary files cleaned up: example.txt",
  "cleaned": true
}
```

### Pause Upload

Pause file upload.

**Request**:
- Method: `POST`
- Path: `/api/v1/upload/{filename}/pause`
- Content Type: `application/json`
- Parameters:
  ```json
  {
    "chunk_index": 5
  }
  ```

**Response**:
```json
{
  "success": true,
  "message": "Upload paused: example.txt"
}
```

### Resume Upload

Resume a paused file upload.

**Request**:
- Method: `POST`
- Path: `/api/v1/upload/{filename}/resume`

**Response**:
```json
{
  "success": true,
  "message": "Upload resumed: example.txt",
  "last_chunk": 5,
  "has_temp_dir": true,
  "cleaned_chunks": 0
}
```

### Get Upload State

Get the upload state of a file.

**Request**:
- Method: `GET`
- Path: `/api/v1/upload/{filename}/state`

**Response**:
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

## WebSocket Events

In addition to REST APIs, the application also provides WebSocket events for real-time communication.

### Client Events

Clients can send the following events:

| Event Name | Description | Data Format |
|------------|-------------|-------------|
| `connect` | Connect to the WebSocket server | None |
| `upload_progress` | Update upload progress | `{"filename": "example.txt", "progress": 50}` |

### Server Events

The server sends the following events:

| Event Name | Description | Data Format |
|------------|-------------|-------------|
| `files_updated` | File list has been updated | `{"files": [...]}` |
| `upload_progress_update` | Upload progress has been updated | `{"filename": "example.txt", "progress": 50}` |
| `upload_state_updated` | Upload state has been updated | `{"filename": "example.txt", "status": "paused", "paused": true}` |

## Error Handling

All APIs return a JSON object containing `success: false` and an `error` field when an error occurs.

Common error responses:

```json
{
  "success": false,
  "error": "File not found: example.txt"
}
```

In development mode, error responses also include detailed error information and stack traces:

```json
{
  "success": false,
  "error": "File not found: example.txt",
  "traceback": "..."
}
```

## Status Codes

The API uses the following HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Request successful |
| 400 | Request parameter error |
| 404 | Requested resource not found |
| 405 | Method not allowed |
| 413 | Request entity too large |
| 500 | Internal server error |
