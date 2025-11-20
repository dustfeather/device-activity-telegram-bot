"""Pytest configuration and shared fixtures."""

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from telegram import Chat, Message, Update, User
from telegram.ext import CallbackContext


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    # Use valid Telegram bot token format: numeric:alphanumeric
    bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    chat_id = "67890"
    monkeypatch.setenv("BOT_TOKEN", bot_token)
    monkeypatch.setenv("CHAT_ID", chat_id)
    return {"BOT_TOKEN": bot_token, "CHAT_ID": chat_id}


@pytest.fixture
def mock_settings(monkeypatch, mock_env_vars):
    """Mock the settings object in all modules that use it."""
    from unittest.mock import MagicMock

    mock_settings_obj = MagicMock()
    mock_settings_obj.bot_token = mock_env_vars["BOT_TOKEN"]
    mock_settings_obj.chat_id = mock_env_vars["CHAT_ID"]

    # Patch settings in all modules that import it
    monkeypatch.setattr("src.config.settings", mock_settings_obj)
    monkeypatch.setattr("src.halt.settings", mock_settings_obj)
    monkeypatch.setattr("src.telegram_client.settings", mock_settings_obj)

    return mock_settings_obj


@pytest.fixture
def mock_httpx_client(monkeypatch, mock_env_vars):
    """Mock httpx.AsyncClient for HTTP calls."""
    mock_response = Mock()
    mock_response.json.return_value = {"ok": True, "result": {"message_id": 1}}
    mock_response.raise_for_status = Mock()

    async def mock_post(*args, **kwargs):
        return mock_response

    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=mock_post)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    # Patch httpx.AsyncClient
    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: mock_client)
    return mock_client


@pytest.fixture
def mock_platform_node(monkeypatch):
    """Mock platform.node() to return a test device name."""
    monkeypatch.setattr("platform.node", lambda: "test-device")
    # Also patch halt.os_name directly
    monkeypatch.setattr("src.halt.os_name", "test-device")


@pytest.fixture
def mock_platform_system(monkeypatch):
    """Mock platform.system() to return a test OS."""

    def _mock_system(os_name="Windows"):
        monkeypatch.setattr("platform.system", lambda: os_name)

    return _mock_system


@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """Mock subprocess.run for shutdown commands."""
    mock_run = Mock()
    monkeypatch.setattr("subprocess.run", mock_run)
    return mock_run


@pytest.fixture
def mock_telegram_update():
    """Create a mock Telegram Update object."""
    user = User(id=12345, first_name="Test", is_bot=False, username="testuser")
    chat = Chat(id=67890, type="private")
    message = Message(message_id=1, date=None, chat=chat, from_user=user, text="/halt")
    update = Update(update_id=1, message=message)
    # Note: Cannot set reply_text directly on frozen Message objects
    # Tests should use patch.object() to mock reply_text when needed
    return update


@pytest.fixture
def mock_telegram_context():
    """Create a mock Telegram CallbackContext object."""
    context = MagicMock(spec=CallbackContext)
    context.args = []
    context.error = None
    return context


@pytest.fixture
def mock_application_builder(monkeypatch):
    """Mock ApplicationBuilder for e2e tests."""
    mock_app = MagicMock()
    mock_builder = MagicMock()
    mock_builder.token.return_value = mock_builder
    mock_builder.build.return_value = mock_app
    monkeypatch.setattr("telegram.ext.ApplicationBuilder", lambda: mock_builder)
    return mock_app, mock_builder
