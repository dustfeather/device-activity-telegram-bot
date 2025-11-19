"""Unit tests for send.py module."""

from unittest.mock import patch

import pytest

from src import send
from src.telegram_client import send_message


class TestSendMessage:
    """Test cases for the send_message() function."""

    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_env_vars, mock_httpx_client):
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
    async def test_send_message_uses_env_vars(self, mock_env_vars, mock_httpx_client):
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
