# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Security
- `/halt` now rejects commands from users outside an allowlist ([#56](https://github.com/dustfeather/device-activity-telegram-bot/issues/56)). Previously the command handler was registered with no sender filter, so any Telegram user who found the bot could shut down the host — `/halt` with no arguments powers off immediately. The check runs before argument parsing and is applied in two places: a `filters.User` filter on the handler, and inside `halt()` itself, because `error_handler` re-invokes `halt()` directly on a timeout retry and would otherwise bypass the filter.

### Added
- `ALLOWED_USER_IDS` setting (optional, comma-separated Telegram user IDs). When unset it defaults to `CHAT_ID`, which in a private chat is the owner's own user ID — existing single-user deployments need no configuration change.
- `tests/test_config.py` covering allowlist resolution and validation.
- Tests asserting an unauthorized sender cannot shut down the host, including via the `error_handler` retry path.

### Changed
- Startup now fails with a clear error when `CHAT_ID` is negative (a group or channel) and `ALLOWED_USER_IDS` is unset, rather than defaulting to a value that would authorize every member of the group.

## [2025-11-19]

### Added
- Comprehensive test suite with pytest
  - Unit tests for `send.py` module (`tests/test_send.py`)
  - Unit tests for `halt.py` module including command handlers, shutdown logic, and error handling (`tests/test_halt.py`)
  - End-to-end tests for complete bot flow with mocked dependencies (`tests/test_e2e.py`)
  - Shared pytest fixtures for mocking environment variables, HTTP requests, and Telegram objects (`tests/conftest.py`)
- `pytest.ini` configuration file for async test support
- `TESTING.md` documentation with detailed test instructions and structure
- `pytest==8.3.4` and `pytest-asyncio==0.24.0` dependencies

### Changed
- Moved testing documentation from `README.md` to dedicated `TESTING.md` file for better organization

## [2024-05-17] - Initial Release

### Added
- `send.py` - Sends Telegram notifications when device is logged into or screen is unlocked
- `halt.py` - Telegram bot that listens for remote shutdown commands via `/halt` command
- Support for Windows, Linux, and macOS shutdown commands
- Device name matching for targeted shutdown commands
- Error handling with automatic retry for timeout errors
- Startup notification when halt monitor begins
