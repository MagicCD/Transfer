# Configuration Guide

This document details all configuration options, validation rules, and default values for the LAN File Transfer Tool.

## Configuration Loading Order

Configurations are loaded in the following order, with later configurations overriding earlier ones:

1. Pydantic model default values
2. Environment-specific configuration (development, production, or test)
3. Environment variables
4. Local configuration (`local_settings.py`, if exists)

## Environment Detection

The application automatically detects the running environment:

- If it's a packaged executable file, it uses the production environment configuration
- Otherwise, it gets the running environment from the `FLASK_ENV` environment variable, defaulting to development
- Possible values: `development`, `production`, `test`

## Configuration Options

### Application Base Configuration

| Option | Type | Default Value | Environment Variable | Description | Validation Rules |
|--------|------|---------------|----------------------|-------------|------------------|
| `SECRET_KEY` | string | `'your-secret-key'` | `SECRET_KEY` | Application secret key, used for session encryption and other security features | Required |
| `SERVER_PORT` | integer | `5000` | `SERVER_PORT` | Server listening port | Required, range: 1024-65535 |
| `DEBUG` | boolean | Development: `True`<br>Production: `False` | `DEBUG` | Whether to enable debug mode | Optional |
| `SECURE_COOKIES` | boolean | Development: `False`<br>Production: `True` | `SECURE_COOKIES` | Whether to enable secure cookies | Optional |

### File Upload Configuration

| Option | Type | Default Value | Environment Variable | Description | Validation Rules |
|--------|------|---------------|----------------------|-------------|------------------|
| `UPLOAD_FOLDER` | string | `'uploads'` | `UPLOAD_FOLDER` | Upload file storage directory | Required, directory will be created if it doesn't exist |
| `TEMP_CHUNKS_DIR` | string | `'uploads/.temp_chunks'` | `TEMP_CHUNKS_DIR` | Temporary chunk file storage directory | Required, directory will be created if it doesn't exist |
| `MAX_CONTENT_LENGTH` | integer | `5 * GB` (5GB) | `MAX_CONTENT_LENGTH` | Maximum upload file size (bytes) | Required, range: 1MB-10GB |
| `CHUNK_SIZE` | integer | `5 * MB` (5MB) | `CHUNK_SIZE` | File chunk size (bytes) | Required, range: 1MB-100MB, must be less than or equal to chunked upload threshold |
| `CHUNKED_UPLOAD_THRESHOLD` | integer | `50 * MB` (50MB) | `CHUNKED_UPLOAD_THRESHOLD` | File size threshold for enabling chunked upload (bytes) | Required, range: 1MB-1GB, must be less than or equal to maximum content length |

### Cache and Temporary File Configuration

| Option | Type | Default Value | Environment Variable | Description | Validation Rules |
|--------|------|---------------|----------------------|-------------|------------------|
| `FILES_CACHE_TTL` | integer | Development: `5`<br>Production: `30` | `FILES_CACHE_TTL` | File list cache time-to-live (seconds) | Required, range: 1-3600 |
| `TEMP_FILES_MAX_AGE` | integer | Development: `2`<br>Production: `24` | `TEMP_FILES_MAX_AGE` | Maximum age of temporary files (hours) | Required, range: 1-168 |

### Logging Configuration

| Option | Type | Default Value | Environment Variable | Description | Validation Rules |
|--------|------|---------------|----------------------|-------------|------------------|
| `LOG_LEVEL` | string | Development: `'DEBUG'`<br>Production: `'INFO'` | `LOG_LEVEL` | Logging level | Required, possible values: `'DEBUG'`, `'INFO'`, `'WARNING'`, `'ERROR'`, `'CRITICAL'` |
| `LOG_FORMAT` | string | `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'` | None | Logging format | Required |

## Environment-Specific Configuration

### Development Environment

| Option | Value |
|--------|-------|
| `DEBUG` | `True` |
| `LOG_LEVEL` | `'DEBUG'` |
| `TEMP_FILES_MAX_AGE` | `2` |
| `FILES_CACHE_TTL` | `5` |

### Production Environment

| Option | Value |
|--------|-------|
| `DEBUG` | `False` |
| `LOG_LEVEL` | `'INFO'` |
| `TEMP_FILES_MAX_AGE` | `24` |
| `FILES_CACHE_TTL` | `30` |
| `SECURE_COOKIES` | `True` |

### Test Environment

| Option | Value |
|--------|-------|
| `DEBUG` | `True` |
| `LOG_LEVEL` | `'DEBUG'` |
| `TEMP_FILES_MAX_AGE` | `1` |
| `FILES_CACHE_TTL` | `1` |
| `UPLOAD_FOLDER` | Temporary directory |
| `TEMP_CHUNKS_DIR` | Temporary directory |

## Local Configuration

You can create a `local_settings.py` file to override any configuration option. This file is not tracked by version control and is suitable for storing local development environment-specific configurations.

Example:

```python
# Debug mode
DEBUG = True

# Custom secret key
SECRET_KEY = 'your-custom-dev-key'

# Custom upload directory
UPLOAD_FOLDER = 'custom/uploads/path'

# Log level
LOG_LEVEL = 'DEBUG'
```

## Environment Variables

You can also set configuration options through environment variables. Create a `.env` file and set environment variables according to the examples in `.env.example`.

Example:

```
SECRET_KEY=your-secret-key-here
SERVER_PORT=5000
FLASK_ENV=development
UPLOAD_FOLDER=uploads
TEMP_CHUNKS_DIR=uploads/.temp_chunks
MAX_CONTENT_LENGTH=5368709120
```

## Benefits of Using Pydantic

Using Pydantic for configuration management has the following benefits:

1. **Type Safety**: All configuration options have clear type annotations, allowing type errors to be caught before runtime
2. **Automatic Validation**: Configuration values are automatically validated according to validation rules, ensuring configuration correctness
3. **Default Values**: Default values can be set for configuration options, simplifying the configuration process
4. **Documentation**: Configuration option definitions include detailed descriptions, making it easy for developers to understand the purpose and limitations of configuration options
5. **Environment-Specific Configuration**: Different configuration values can be set for different environments, simplifying environment switching
