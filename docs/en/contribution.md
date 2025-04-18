# Contribution Guidelines

Thank you for considering contributing to the LAN File Transfer Tool! This document provides detailed guidelines for participating in project development.

## Contribution Process

### 1. Preparation

1. Fork the project repository on GitHub
2. Clone the forked repository to your local machine
   ```bash
   git clone https://github.com/YOUR_USERNAME/Transfer.git
   cd Transfer
   ```
3. Add the upstream repository
   ```bash
   git remote add upstream https://github.com/MagicCD/Transfer.git
   ```
4. Create a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

### 2. Development Environment Setup

1. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```
3. Install pre-commit hooks
   ```bash
   pre-commit install
   ```

### 3. Development Standards

#### Code Style

- Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation, not tabs
- Line length should not exceed 100 characters
- Use meaningful variable and function names
- Add appropriate comments and docstrings

#### Commit Standards

- Commit messages should be concise and describe the main content of the commit
- Use present tense ("Add feature" not "Added feature")
- The first line is the title, not exceeding 50 characters
- If detailed explanation is needed, leave a blank line after the title, then add a detailed description

Example:
```
Add chunked upload progress tracking

- Add real-time progress tracking for chunked uploads
- Implement WebSocket events for progress updates
- Update UI to display progress bar for each chunk
```

### 4. Testing

- Write tests for new features or bug fixes
- Ensure all tests pass
- Test coverage should be at least 80%

Run tests:
```bash
pytest
```

Check test coverage:
```bash
pytest --cov=app
```

### 5. Submit Changes

1. Add your changes to the staging area
   ```bash
   git add .
   ```
2. Commit your changes
   ```bash
   git commit -m "Your commit message"
   ```
3. Push your local branch to your forked repository
   ```bash
   git push origin feature/your-feature-name
   ```
4. Create a Pull Request on GitHub

### 6. Code Review

- Wait patiently for code review
- Make changes based on review comments
- If you need to update the Pull Request, simply push changes to the same branch

## Project Structure

Understanding the project structure will help you contribute code better:

```
app/
├── api/                  # API layer
│   ├── v1/             # API version control
│   └── middlewares/    # Middlewares
├── core/                 # Core functionality modules
│   ├── exceptions/      # Unified exception handling
│   ├── interfaces/      # Abstract interface definitions
│   └── validators/      # Data validators
├── services/             # Service layer
│   ├── file/            # File services
│   ├── upload/          # Upload services
│   └── cache/           # Cache services
├── utils/                # Utility functions
└── config/               # Configuration management
    └── models.py        # Configuration models

static/                   # Static resources
templates/                # HTML templates
tests/                    # Test code
docs/                     # Documentation
```

## Feature Development Guidelines

### Adding New APIs

1. Create a new module in the `app/api/v1/` directory or add new routes to existing modules
2. Follow RESTful API design principles
3. Use the `api_error_handler` decorator to handle exceptions
4. Update API documentation

### Modifying the Frontend Interface

1. Frontend code is located in the `static/js/` and `templates/` directories
2. Follow existing code style and organization
3. Ensure compatibility with mainstream browsers
4. Test display effects on different devices and screen sizes

### Adding New Configuration Options

1. Add new configuration options to the appropriate configuration model in `app/config/models.py`
2. Add appropriate type annotations and validation rules
3. Provide reasonable default values
4. Update configuration documentation

## Documentation Contributions

Documentation is located in the `docs/` directory, divided into Chinese and English versions. If you modify or add features, please update the corresponding documentation.

## Reporting Bugs

If you find a bug but don't have time to fix it, please submit an Issue on GitHub, including:

1. Detailed description of the bug
2. Steps to reproduce
3. Expected behavior and actual behavior
4. Your environment information (operating system, Python version, etc.)
5. Relevant logs or error messages

## Suggesting Features

If you have ideas for new features, please submit an Issue on GitHub, describing:

1. The feature you want
2. Why this feature is valuable to the project
3. How to implement it (if you have ideas)

## Code of Conduct

Please follow the project's code of conduct, maintaining respect and professionalism. We welcome contributions from everyone, regardless of background and experience level.

## License

By contributing code, you agree that your contribution will be licensed under the MIT License.
