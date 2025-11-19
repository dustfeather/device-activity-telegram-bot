"""End-to-end tests for the halt.py bot functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Chat, Message, Update, User
from telegram.error import TimedOut
from telegram.ext import Application, CallbackContext

from src import halt


class TestE2EHaltFlow:
    """End-to-end tests for the /halt command flow."""

    @pytest.mark.asyncio
    async def test_e2e_halt_no_args_flow(
        self, mock_env_vars, mock_subprocess_run, mock_platform_node, mock_httpx_client
    ):
        """Test complete e2e flow: /halt command with no args."""
        # Create a real Update object
        user = User(id=12345, first_name="Test", is_bot=False, username="testuser")
        chat = Chat(id=67890, type="private")
        message = Message(message_id=1, date=None, chat=chat, from_user=user, text="/halt")
        update = Update(update_id=1, message=message)

        # Create a mock context
        context = MagicMock(spec=CallbackContext)
        context.args = []

        # Mock the message reply at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            # Execute the halt handler
            await halt.halt(update, context)

            # Verify the reply was sent
            assert mock_reply.called
            reply_text = mock_reply.call_args[0][0]
            assert "Shutting down all machines" in reply_text

        # Verify shutdown was called
        assert mock_subprocess_run.called

    @pytest.mark.asyncio
    async def test_e2e_halt_with_device_flow(
        self, mock_env_vars, mock_subprocess_run, mock_platform_node, mock_httpx_client
    ):
        """Test complete e2e flow: /halt command with matching device name."""
        # Create a real Update object
        user = User(id=12345, first_name="Test", is_bot=False, username="testuser")
        chat = Chat(id=67890, type="private")
        message = Message(
            message_id=1, date=None, chat=chat, from_user=user, text="/halt test-device"
        )
        update = Update(update_id=1, message=message)

        # Create a mock context
        context = MagicMock(spec=CallbackContext)
        context.args = ["test-device"]

        # Mock the message reply at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            # Execute the halt handler
            await halt.halt(update, context)

            # Verify the reply was sent
            assert mock_reply.called
            reply_text = mock_reply.call_args[0][0]
            assert "Shutting down test-device" in reply_text

        # Verify shutdown was called
        assert mock_subprocess_run.called

    @pytest.mark.asyncio
    async def test_e2e_halt_with_wrong_device_flow(
        self, mock_env_vars, mock_subprocess_run, mock_platform_node, mock_httpx_client
    ):
        """Test complete e2e flow: /halt command with non-matching device name."""
        # Create a real Update object
        user = User(id=12345, first_name="Test", is_bot=False, username="testuser")
        chat = Chat(id=67890, type="private")
        message = Message(
            message_id=1, date=None, chat=chat, from_user=user, text="/halt wrong-device"
        )
        update = Update(update_id=1, message=message)

        # Create a mock context
        context = MagicMock(spec=CallbackContext)
        context.args = ["wrong-device"]

        # Mock the message reply at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            # Execute the halt handler
            await halt.halt(update, context)

            # Verify the reply was sent
            assert mock_reply.called
            reply_text = mock_reply.call_args[0][0]
            assert "does not match" in reply_text

        # Verify shutdown was NOT called
        assert not mock_subprocess_run.called

    @pytest.mark.asyncio
    async def test_e2e_application_setup(self, mock_env_vars, mock_httpx_client):
        """Test e2e application setup and configuration."""
        with patch("src.halt.ApplicationBuilder") as mock_builder_class:
            mock_app = MagicMock(spec=Application)
            mock_builder = MagicMock()
            mock_builder.token.return_value = mock_builder
            mock_builder.build.return_value = mock_app
            mock_builder_class.return_value = mock_builder

            # Call main (but don't actually start polling)
            with patch.object(mock_app, "run_polling"):
                halt.main()

            # Verify ApplicationBuilder was instantiated
            assert mock_builder_class.called

            # Verify token was set
            mock_builder.token.assert_called_once_with(mock_env_vars["BOT_TOKEN"])

            # Verify application was built
            mock_builder.build.assert_called_once()

            # Verify handlers were registered
            assert mock_app.add_handler.called
            assert mock_app.add_error_handler.called

    @pytest.mark.asyncio
    async def test_e2e_error_retry_flow(
        self, mock_env_vars, mock_subprocess_run, mock_platform_node, mock_httpx_client
    ):
        """Test e2e error handling and retry flow."""
        # Create a real Update object
        user = User(id=12345, first_name="Test", is_bot=False, username="testuser")
        chat = Chat(id=67890, type="private")
        message = Message(message_id=1, date=None, chat=chat, from_user=user, text="/halt")
        update = Update(update_id=1, message=message)

        # Create a mock context with TimedOut error
        context = MagicMock(spec=CallbackContext)
        context.args = []
        context.error = TimedOut("Connection timeout")

        # Mock the message reply at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            # Mock asyncio.sleep to avoid actual delays
            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await halt.error_handler(update, context)

                # Verify sleep was called with 5 seconds
                mock_sleep.assert_called_once_with(5)

                # Verify halt was retried (reply_text should be called)
                assert mock_reply.called

    @pytest.mark.asyncio
    async def test_e2e_startup_message(self, mock_env_vars, mock_httpx_client, mock_platform_node):
        """Test e2e startup message sending."""
        # Test the startup_notification function
        await halt.startup_notification()

        # Verify send_message was called with correct message
        assert mock_httpx_client.post.called
        call_args = mock_httpx_client.post.call_args
        assert "test-device" in call_args[1]["data"]["text"]
        assert "started halt monitor" in call_args[1]["data"]["text"]
