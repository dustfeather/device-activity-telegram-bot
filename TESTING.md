# Testing Guide

This project includes comprehensive unit and end-to-end tests powered by pytest. All external dependencies (Telegram API, HTTP requests, system commands) are mocked so the suite can run without network access or elevated privileges.

## Prerequisites

```sh
virtualenv venv
venv/bin/pip install -r requirements.txt
```

## Running Tests

```sh
# Run the entire suite
venv/bin/pytest

# Verbose output
venv/bin/pytest -v

# Target a specific module
venv/bin/pytest tests/test_send.py
venv/bin/pytest tests/test_halt.py

Note: The project uses a `src/` layout, so the source files are located in `src/halt.py` and `src/send.py`.
venv/bin/pytest tests/test_e2e.py

# Generate a coverage report
venv/bin/pytest --cov=. --cov-report=html
```

## Test Structure

- `tests/test_send.py` – Unit tests for the `send()` helper.
- `tests/test_halt.py` – Unit tests for the halt handler, shutdown logic, and retry handling.
- `tests/test_e2e.py` – Mocked end-to-end flows covering `/halt` usage and application setup.
- `tests/conftest.py` – Shared fixtures for environment variables, HTTP mocks, and Telegram objects.

## Tips

- Use `pytest -k "<keyword>"` to focus on specific scenarios.
- Combine `-k` with `-vv` for more granular logging when debugging failures.
- The coverage HTML output is written to `htmlcov/index.html`.
