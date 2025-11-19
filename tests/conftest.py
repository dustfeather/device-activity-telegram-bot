"""
Pytest configuration and shared fixtures.
"""
import os
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from telegram import Update, Message, Chat, User
from telegram.ext import CallbackContext


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    # Use valid Telegram bot token format: numeric:alphanumeric
    monkeypatch.setenv('BOT_TOKEN', '123456789:ABCdefGHIjklMNOpqrsTUVwxyz')
    monkeypatch.setenv('CHAT_ID', '67890')
    return {
        'BOT_TOKEN': '123456789:ABCdefGHIjklMNOpqrsTUVwxyz',
        'CHAT_ID': '67890'
    }


@pytest.fixture
def mock_requests_post(monkeypatch):
    """Mock requests.post for HTTP calls."""
    mock_response = Mock()
    mock_response.json.return_value = {'ok': True, 'result': {'message_id': 1}}
    mock_post = Mock(return_value=mock_response)
    monkeypatch.setattr('requests.post', mock_post)
    return mock_post


@pytest.fixture
def mock_platform_node(monkeypatch):
    """Mock platform.node() to return a test device name."""
    # Patch both platform.node and halt.os_name since os_name is set at module load time
    monkeypatch.setattr('platform.node', lambda: 'test-device')
    # Also patch halt.os_name directly in case the module was already loaded
    try:
        import sys
        import os
        src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        import halt
        monkeypatch.setattr('halt.os_name', 'test-device')
    except ImportError:
        pass


@pytest.fixture
def mock_platform_system(monkeypatch):
    """Mock platform.system() to return a test OS."""
    def _mock_system(os_name='Windows'):
        monkeypatch.setattr('platform.system', lambda: os_name)
    return _mock_system


@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """Mock subprocess.run for shutdown commands."""
    mock_run = Mock()
    monkeypatch.setattr('subprocess.run', mock_run)
    return mock_run


@pytest.fixture
def mock_telegram_update():
    """Create a mock Telegram Update object."""
    user = User(id=12345, first_name='Test', is_bot=False, username='testuser')
    chat = Chat(id=67890, type='private')
    message = Message(
        message_id=1,
        date=None,
        chat=chat,
        from_user=user,
        text='/halt'
    )
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
    monkeypatch.setattr('telegram.ext.ApplicationBuilder', lambda: mock_builder)
    return mock_app, mock_builder

