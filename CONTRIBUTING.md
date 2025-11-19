# Contributing to Device Activity Telegram Bot

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- A Telegram bot token (for testing, see [README.md](README.md))

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

3. **Run tests**
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

4. **Ensure all tests pass**
   - All existing tests must pass
   - New code should have test coverage
   - Tests should run on both Windows and Linux (CI will verify)

### Code Style

This project follows Python PEP 8 style guidelines with the following conventions:

- **Indentation**: 2 spaces (configured in `.editorconfig`)
- **Line endings**: LF (Unix-style)
- **Maximum line length**: 88 characters (Black default)
- **Import order**: Standard library, third-party, local imports

The project uses `.editorconfig` for consistent formatting. Most editors support this automatically.

**Code Style Checklist:**
- [ ] Use 2 spaces for indentation
- [ ] Use LF line endings
- [ ] Remove trailing whitespace
- [ ] Add final newline to files
- [ ] Follow PEP 8 naming conventions
- [ ] Add docstrings for functions and classes
- [ ] Keep functions focused and small

### Testing Requirements

- **All new features must include tests**
- **All bug fixes must include regression tests**
- **Test coverage should be maintained or improved**
- **Tests must pass on both Windows and Linux**

See [TESTING.md](TESTING.md) for detailed testing guidelines.

**Test Structure:**
- Unit tests go in `tests/test_*.py`
- Use descriptive test names: `test_function_name_scenario`
- Mock external dependencies (HTTP, Telegram API, system commands)
- Use pytest fixtures from `tests/conftest.py`

### Documentation

- Update `README.md` if you change usage or installation
- Update `CHANGELOG.md` for user-facing changes
- Add docstrings to new functions and classes
- Update `TESTING.md` if testing procedures change

## Submitting Changes

### Pull Request Process

1. **Ensure your code is ready**
   - [ ] All tests pass locally
   - [ ] Code follows style guidelines
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
│   ├── halt.py          # Main bot application
│   └── send.py          # Send notification script
├── requirements.txt     # Runtime dependencies
├── requirements-dev.txt # Development dependencies
├── tests/              # Test suite
│   ├── conftest.py     # Shared fixtures
│   ├── test_send.py    # Tests for send.py
│   ├── test_halt.py    # Tests for halt.py
│   └── test_e2e.py     # End-to-end tests
├── .github/
│   └── workflows/      # CI/CD workflows
└── docs/               # Additional documentation
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
