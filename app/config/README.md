# Configuration Management

This directory contains the configuration management system for the application.

## Documentation

Detailed documentation about the configuration system is available in the following locations:

- [Chinese Configuration Guide](../../docs/zh_CN/configuration.md)
- [English Configuration Guide](../../docs/en/configuration.md)

## Structure

- `__init__.py` - Main configuration loader
- `models.py` - Pydantic configuration models
- `local_settings.py` - Local development overrides (not in version control)
- `CONFIG.md` - Configuration documentation (deprecated, see docs/ directory instead)

## Configuration Loading Order

Configurations are loaded in the following order, with later configurations overriding earlier ones:

1. Pydantic model default values
2. Environment-specific configuration (development, production, or test)
3. Environment variables
4. Local configuration (`local_settings.py`, if exists)

## Environment Variables

The application uses environment variables for configuration. You can set these in a `.env` file in the project root.

See `.env.example` for available configuration options.

## Local Settings

For local development, you can create a `local_settings.py` file. This file is not tracked by version control and can contain environment-specific overrides.

## Environment Selection

The environment is determined by:

1. For packaged applications: Always uses production
2. For development: Uses the `FLASK_ENV` environment variable, defaulting to 'development'
