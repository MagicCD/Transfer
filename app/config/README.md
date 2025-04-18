# Configuration Management

This directory contains the configuration management system for the application.

## Structure

- `__init__.py` - Main configuration loader
- `config_validator.py` - Configuration validation
- `local_settings.py` - Local development overrides (not in version control)
- `local_settings.py.example` - Example local settings file
- `settings/` - Environment-specific configuration files
  - `base.py` - Base configuration shared by all environments
  - `constants.py` - Constants used across the application
  - `development.py` - Development environment configuration
  - `production.py` - Production environment configuration
  - `test.py` - Test environment configuration

## Environment Variables

The application uses environment variables for configuration. You can set these in a `.env` file in the project root.

See `.env.example` for available configuration options.

## Local Settings

For local development, you can create a `local_settings.py` file based on the example file. This file is not tracked by version control and can contain environment-specific overrides.

## Configuration Loading Order

1. Base configuration (`settings/base.py`)
2. Environment-specific configuration (`settings/development.py`, `settings/production.py`, or `settings/test.py`)
3. Local settings (`local_settings.py`)
4. Configuration validation

## Environment Selection

The environment is determined by:

1. For packaged applications: Always uses production
2. For development: Uses the `FLASK_ENV` environment variable, defaulting to 'development'
