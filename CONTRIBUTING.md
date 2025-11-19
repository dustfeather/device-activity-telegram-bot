# Contributing to Device Activity Telegram Bot

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Getting Started

### Prerequisites

- Python 3.14 or higher
- Git
- A Telegram bot token (for testing, see [README.md](README.md))

### Python Version Management

This project requires Python 3.14. If you need to manage multiple Python versions:

#### Windows (using pyenv-win)

1. **Install pyenv-win**:
   ```powershell
   Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
   ```

2. **Install Python 3.14**:
   ```powershell
   pyenv install 3.14.0
   pyenv local 3.14.0  # Set for this project
   ```

3. **Verify installation**:
   ```powershell
   python --version  # Should show Python 3.14.x
   ```

#### Linux/macOS (using pyenv)

1. **Install pyenv** (if not already installed):
   ```bash
   # macOS (using Homebrew)
   brew install pyenv
   
   # Linux (using pyenv-installer)
   curl https://pyenv.run | bash
   ```

2. **Install Python 3.14**:
   ```bash
   pyenv install 3.14.0
   pyenv local 3.14.0  # Set for this project
   ```

3. **Verify installation**:
   ```bash
   python --version  # Should show Python 3.14.x
   ```

### Development Setup

1. **Fork and clone the repository**
   ```sh
   git clone https://github.com/your-username/device-activity-telegram-bot.git
   cd device-activity-telegram-bot
   ```

2. **Create a virtual environment**
   ```sh
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```sh
   # Install runtime dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (handles platform-specific packages)
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```sh
   cp .env.example .env
   # Edit .env with your BOT_TOKEN and CHAT_ID
   ```

## Development Workflow

### Making Changes

1. **Create a branch**
   ```sh
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**
   - Follow the code style guidelines (see below)
   - Write or update tests for new functionality
   - Update documentation as needed
   - Add type hints to all functions

3. **Run code quality checks**
   ```sh
   # Lint code
   ruff check src/ tests/
   
   # Format code
   ruff format src/ tests/
   
   # Type check
   mypy src/
   ```

4. **Run tests**
   ```sh
   # Run all tests
   pytest
   
   # Run with verbose output
   pytest -v
   
   # Run specific test file
   pytest tests/test_halt.py
   
   # Check test coverage
   pytest --cov=. --cov-report=html
   ```

5. **Ensure all checks pass**
   - All tests must pass
   - Code must pass linting (ruff)
   - Code must pass type checking (mypy)
   - Code must be properly formatted (ruff format)
   - New code should have test coverage

### Code Style

This project uses modern Python tooling for code quality:

- **ruff**: Fast linting and code formatting (replaces flake8, isort, black)
- **mypy**: Static type checking

**Code Style Guidelines:**
- **Indentation**: 4 spaces
- **Line endings**: LF (Unix-style)
- **Maximum line length**: 100 characters
- **Import order**: Standard library, third-party, local imports (enforced by ruff)
- **Type hints**: Required for all functions and methods
- **Docstrings**: Required for all public functions and classes

**Code Style Checklist:**
- [ ] Code passes `ruff check`
- [ ] Code is formatted with `ruff format`
- [ ] Type hints added to all functions
- [ ] Type checking passes with `mypy`
- [ ] Docstrings added for functions and classes
- [ ] Follow PEP 8 naming conventions

### Type Hints

All functions and methods must include type hints:

```python
from typing import Any

async def send_message(message: str) -> dict[str, Any]:
    """Send a message via Telegram Bot API."""
    ...
```

### Testing Requirements

- **All new features must include tests**
- **All bug fixes must include regression tests**
- **Test coverage should be maintained or improved**
- **Tests must pass on both Windows and Linux**
- **Tests must handle async functions properly**

See [TESTING.md](TESTING.md) for detailed testing guidelines.

**Test Structure:**
- Unit tests go in `tests/test_*.py`
- Use descriptive test names: `test_function_name_scenario`
- Mock external dependencies (HTTP, Telegram API, system commands)
- Use pytest fixtures from `tests/conftest.py`
- Use `@pytest.mark.asyncio` for async tests

### Documentation

- Update `README.md` if you change usage or installation
- Update `CHANGELOG.md` for user-facing changes
- Add docstrings to new functions and classes
- Update `TESTING.md` if testing procedures change

## Submitting Changes

### Pull Request Process

1. **Ensure your code is ready**
   - [ ] All tests pass locally
   - [ ] Code passes linting (`ruff check`)
   - [ ] Code is formatted (`ruff format`)
   - [ ] Type checking passes (`mypy`)
   - [ ] Documentation is updated
   - [ ] CHANGELOG.md is updated (if applicable)

2. **Push your branch**
   ```sh
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**
   - Use a clear, descriptive title
   - Provide a detailed description of changes
   - Reference any related issues
   - Include screenshots or examples if applicable

4. **Respond to feedback**
   - Address review comments promptly
   - Make requested changes in new commits
   - Keep the PR focused on a single change

### Commit Messages

Write clear, descriptive commit messages:

```
feat: Add device name validation for /halt command

- Validate device names before shutdown
- Add error handling for invalid device names
- Update tests to cover new validation logic

Fixes #123
```

**Commit Message Format:**
- Use conventional commit prefixes: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- First line should be concise (50 chars or less)
- Add detailed description if needed
- Reference issues with `Fixes #123` or `Closes #123`

## Project Structure

```
device-activity-telegram-bot/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management (pydantic-settings)
│   ├── telegram_client.py # Shared Telegram API client
│   ├── halt.py            # Main bot application
│   └── send.py            # Send notification script
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Development dependencies
├── pyproject.toml         # Project configuration (ruff, mypy, setuptools)
├── tests/                 # Test suite
│   ├── conftest.py        # Shared fixtures
│   ├── test_send.py       # Tests for send.py
│   ├── test_halt.py       # Tests for halt.py
│   └── test_e2e.py        # End-to-end tests
├── .github/
│   └── workflows/         # CI/CD workflows
└── docs/                  # Additional documentation
```

## Areas for Contribution

We welcome contributions in these areas:

- **Bug fixes**: Report or fix bugs
- **Features**: New functionality (discuss in issues first)
- **Tests**: Improve test coverage
- **Documentation**: Improve clarity and completeness
- **Code quality**: Refactoring and improvements
- **Cross-platform support**: Ensure compatibility on Windows and Linux

## Questions?

- Open an issue for bug reports or feature requests
- Check existing issues and discussions
- Review the [README.md](README.md) and [TESTING.md](TESTING.md)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the project
- Help others learn and contribute

Thank you for contributing! 🎉
