"""Unit tests for send.py module."""

from unittest.mock import patch

import pytest

from src import send
from src.telegram_client import send_message


class TestSendMessage:
    """Test cases for the send_message() function."""

    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_env_vars, mock_httpx_client, mock_settings):
        """Test successful message sending."""
        message = "Test message"
        result = await send_message(message)

        # Verify httpx client was used
        assert mock_httpx_client.post.called
        call_args = mock_httpx_client.post.call_args

        # Verify URL construction
        expected_url = f"https://api.telegram.org/bot{mock_env_vars['BOT_TOKEN']}/sendMessage"
        assert call_args[0][0] == expected_url

        # Verify data payload
        assert call_args[1]["data"]["chat_id"] == mock_env_vars["CHAT_ID"]
        assert call_args[1]["data"]["text"] == message

        # Verify return value
        assert result == {"ok": True, "result": {"message_id": 1}}

    @pytest.mark.asyncio
    async def test_send_message_with_empty_message(self, mock_env_vars, mock_httpx_client):
        """Test sending an empty message."""
        message = ""
        await send_message(message)

        assert mock_httpx_client.post.called
        call_args = mock_httpx_client.post.call_args
        assert call_args[1]["data"]["text"] == ""

    @pytest.mark.asyncio
    async def test_send_message_uses_env_vars(
        self, mock_env_vars, mock_httpx_client, mock_settings
    ):
        """Test that send_message() correctly uses environment variables."""
        message = "Test"
        await send_message(message)

        call_args = mock_httpx_client.post.call_args
        expected_url = f"https://api.telegram.org/bot{mock_env_vars['BOT_TOKEN']}/sendMessage"
        assert call_args[0][0] == expected_url
        assert call_args[1]["data"]["chat_id"] == mock_env_vars["CHAT_ID"]

    @pytest.mark.asyncio
    async def test_send_message_http_error(self, mock_env_vars, mock_httpx_client):
        """Test handling of HTTP errors."""
        import httpx

        # Mock a failed response
        mock_httpx_client.post.side_effect = httpx.HTTPStatusError(
            "Bad Request",
            request=httpx.Request("POST", "https://api.telegram.org"),
            response=httpx.Response(400),
        )

        with pytest.raises(httpx.HTTPStatusError):
            await send_message("Test message")

    @pytest.mark.asyncio
    @patch("platform.node")
    async def test_main_execution(self, mock_node, mock_env_vars, mock_httpx_client):
        """Test the main execution block of send.py."""
        mock_node.return_value = "test-device"

        # Test main function
        await send.main()

        # Verify send_message was called with correct message
        assert mock_httpx_client.post.called
        call_args = mock_httpx_client.post.call_args
        assert "test-device" in call_args[1]["data"]["text"]
        assert "logged into" in call_args[1]["data"]["text"]


class TestTelegramClientValidation:
    """Test cases for telegram_client.py validation logic."""

    @pytest.mark.asyncio
    async def test_invalid_bot_token_format_missing_colon(self, mock_httpx_client):
        """Test that invalid bot token format (missing colon) raises ValueError."""
        from unittest.mock import MagicMock

        mock_settings = MagicMock()
        mock_settings.bot_token = "123456789ABCdefGHIjklMNOpqrsTUVwxyz"  # Missing colon
        mock_settings.chat_id = "67890"

        with patch("src.telegram_client.settings", mock_settings):
            with pytest.raises(ValueError, match="Invalid BOT_TOKEN format"):
                await send_message("Test message")

    @pytest.mark.asyncio
    async def test_invalid_bot_token_format_invalid_chars(self, mock_httpx_client):
        """Test that invalid bot token format (invalid characters) raises ValueError."""
        from unittest.mock import MagicMock

        mock_settings = MagicMock()
        mock_settings.bot_token = "123456789:ABC@def"  # Invalid character @
        mock_settings.chat_id = "67890"

        with patch("src.telegram_client.settings", mock_settings):
            with pytest.raises(ValueError, match="Invalid BOT_TOKEN format"):
                await send_message("Test message")

    @pytest.mark.asyncio
    async def test_invalid_bot_token_format_no_numbers(self, mock_httpx_client):
        """Test that invalid bot token format (no numbers before colon) raises ValueError."""
        from unittest.mock import MagicMock

        mock_settings = MagicMock()
        mock_settings.bot_token = "ABC:defGHIjklMNOpqrsTUVwxyz"  # No numbers before colon
        mock_settings.chat_id = "67890"

        with patch("src.telegram_client.settings", mock_settings):
            with pytest.raises(ValueError, match="Invalid BOT_TOKEN format"):
                await send_message("Test message")

    @pytest.mark.asyncio
    async def test_invalid_chat_id_format_non_numeric(self, mock_httpx_client):
        """Test that invalid chat_id format (non-numeric) raises ValueError."""
        from unittest.mock import MagicMock

        mock_settings = MagicMock()
        mock_settings.bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        mock_settings.chat_id = "abc123"  # Non-numeric

        with patch("src.telegram_client.settings", mock_settings):
            with pytest.raises(ValueError, match="Invalid CHAT_ID format"):
                await send_message("Test message")

    @pytest.mark.asyncio
    async def test_invalid_chat_id_format_with_letters(self, mock_httpx_client):
        """Test that invalid chat_id format (contains letters) raises ValueError."""
        from unittest.mock import MagicMock

        mock_settings = MagicMock()
        mock_settings.bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        mock_settings.chat_id = "67890abc"  # Contains letters

        with patch("src.telegram_client.settings", mock_settings):
            with pytest.raises(ValueError, match="Invalid CHAT_ID format"):
                await send_message("Test message")

    @pytest.mark.asyncio
    async def test_valid_negative_chat_id(self, mock_httpx_client):
        """Test that negative chat_id (for groups) is valid."""
        from unittest.mock import MagicMock

        mock_settings_obj = MagicMock()
        mock_settings_obj.bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        mock_settings_obj.chat_id = "-123456789"  # Negative for groups

        with patch("src.telegram_client.settings", mock_settings_obj):
            await send_message("Test message")
            assert mock_httpx_client.post.called

    @pytest.mark.asyncio
    async def test_token_url_encoding(self, mock_httpx_client):
        """Test that token is properly URL-encoded while preserving colon."""
        from unittest.mock import MagicMock

        # Valid token with allowed special characters (hyphen and underscore)
        mock_settings_obj = MagicMock()
        mock_settings_obj.bot_token = "123456789:ABC-def_GHI"  # Valid token with allowed chars
        mock_settings_obj.chat_id = "67890"

        with patch("src.telegram_client.settings", mock_settings_obj):
            await send_message("Test message")
            call_args = mock_httpx_client.post.call_args
            url = call_args[0][0]
            # Verify URL contains the token (colon should be preserved, not encoded)
            assert "123456789:ABC-def_GHI" in url
            assert url.startswith("https://api.telegram.org/bot")
