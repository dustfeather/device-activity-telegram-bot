"""Unit tests for halt.py module."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpcore
import pytest
from telegram.error import TimedOut

from src import halt


class TestShutdownMachine:
    """Test cases for shutdown_machine() function."""

    def test_shutdown_windows(self, mock_subprocess_run, mock_platform_system):
        """Test shutdown command on Windows."""
        mock_platform_system("Windows")

        halt.shutdown_machine()

        assert mock_subprocess_run.called
        call_args = mock_subprocess_run.call_args
        assert call_args[0][0] == ["shutdown", "/s", "/f", "/t", "0"]

    def test_shutdown_linux(self, mock_subprocess_run, mock_platform_system):
        """Test shutdown command on Linux."""
        mock_platform_system("Linux")

        halt.shutdown_machine()

        assert mock_subprocess_run.called
        call_args = mock_subprocess_run.call_args
        assert call_args[0][0] == ["sudo", "shutdown", "now"]

    def test_shutdown_darwin(self, mock_subprocess_run, mock_platform_system):
        """Test shutdown command on macOS (Darwin)."""
        mock_platform_system("Darwin")

        halt.shutdown_machine()

        assert mock_subprocess_run.called
        call_args = mock_subprocess_run.call_args
        assert call_args[0][0] == ["sudo", "shutdown", "now"]


class TestHaltCommand:
    """Test cases for the halt() command handler."""

    @pytest.mark.asyncio
    async def test_halt_no_args(
        self, mock_telegram_update, mock_telegram_context, mock_subprocess_run, mock_platform_node
    ):
        """Test /halt command with no arguments."""
        mock_telegram_context.args = []

        # Mock reply_text at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            await halt.halt(mock_telegram_update, mock_telegram_context)

            # Verify reply was sent
            assert mock_reply.called
            reply_text = mock_reply.call_args[0][0]
            assert "Shutting down all machines" in reply_text

        # Verify shutdown was called
        assert mock_subprocess_run.called

    @pytest.mark.asyncio
    async def test_halt_with_matching_device(
        self, mock_telegram_update, mock_telegram_context, mock_subprocess_run, mock_platform_node
    ):
        """Test /halt command with matching device name."""
        mock_telegram_context.args = ["test-device"]

        # Mock reply_text at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            await halt.halt(mock_telegram_update, mock_telegram_context)

            # Verify reply was sent
            assert mock_reply.called
            reply_text = mock_reply.call_args[0][0]
            assert "Shutting down test-device" in reply_text

        # Verify shutdown was called
        assert mock_subprocess_run.called

    @pytest.mark.asyncio
    async def test_halt_with_non_matching_device(
        self, mock_telegram_update, mock_telegram_context, mock_subprocess_run, mock_platform_node
    ):
        """Test /halt command with non-matching device name."""
        mock_telegram_context.args = ["other-device"]

        # Mock reply_text at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            await halt.halt(mock_telegram_update, mock_telegram_context)

            # Verify reply was sent
            assert mock_reply.called
            reply_text = mock_reply.call_args[0][0]
            assert "does not match" in reply_text

        # Verify shutdown was NOT called
        assert not mock_subprocess_run.called

    @pytest.mark.asyncio
    async def test_halt_with_multiple_args(
        self, mock_telegram_update, mock_telegram_context, mock_subprocess_run
    ):
        """Test /halt command with multiple arguments (invalid usage)."""
        mock_telegram_context.args = ["arg1", "arg2"]

        # Mock reply_text at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            await halt.halt(mock_telegram_update, mock_telegram_context)

            # Verify usage message was sent
            assert mock_reply.called
            reply_text = mock_reply.call_args[0][0]
            assert "Usage: /halt [DEVICENAME]" in reply_text

        # Verify shutdown was NOT called
        assert not mock_subprocess_run.called


class TestErrorHandler:
    """Test cases for the error_handler() function."""

    @pytest.mark.asyncio
    async def test_error_handler_timed_out(
        self, mock_telegram_update, mock_telegram_context, mock_subprocess_run, mock_platform_node
    ):
        """Test error handler with TimedOut exception."""
        mock_telegram_context.error = TimedOut("Connection timeout")
        mock_telegram_context.args = []

        # Mock reply_text at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await halt.error_handler(mock_telegram_update, mock_telegram_context)

                # Verify sleep was called
                mock_sleep.assert_called_once_with(5)

                # Verify halt was called after retry
                assert mock_reply.called

    @pytest.mark.asyncio
    async def test_error_handler_connect_timeout(
        self, mock_telegram_update, mock_telegram_context, mock_subprocess_run, mock_platform_node
    ):
        """Test error handler with httpcore.ConnectTimeout exception."""
        mock_telegram_context.error = httpcore.ConnectTimeout("Connection timeout")
        mock_telegram_context.args = []

        # Mock reply_text at class level since Message objects are frozen
        with patch("telegram.Message.reply_text", new_callable=AsyncMock) as mock_reply:
            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await halt.error_handler(mock_telegram_update, mock_telegram_context)

                # Verify sleep was called
                mock_sleep.assert_called_once_with(5)

                # Verify halt was called after retry
                assert mock_reply.called

    @pytest.mark.asyncio
    async def test_error_handler_other_exception(self, mock_telegram_update, mock_telegram_context):
        """Test error handler with other exception types."""
        mock_telegram_context.error = ValueError("Some other error")

        # Should raise the exception
        with pytest.raises(ValueError):
            await halt.error_handler(mock_telegram_update, mock_telegram_context)


class TestMainFunction:
    """Test cases for the main() function."""

    @patch("src.halt.ApplicationBuilder")
    def test_main_creates_application(self, mock_builder, mock_env_vars):
        """Test that main() creates and configures the application."""
        mock_app = MagicMock()
        mock_builder_instance = MagicMock()
        mock_builder_instance.token.return_value = mock_builder_instance
        mock_builder_instance.build.return_value = mock_app
        mock_builder.return_value = mock_builder_instance

        halt.main()

        # Verify ApplicationBuilder was called
        assert mock_builder.called
        mock_builder_instance.token.assert_called_once_with(mock_env_vars["BOT_TOKEN"])
        mock_builder_instance.build.assert_called_once()

        # Verify handlers were added
        assert mock_app.add_handler.called
        assert mock_app.add_error_handler.called

        # Verify polling was started
        mock_app.run_polling.assert_called_once()

    @patch("src.halt.ApplicationBuilder")
    def test_main_registers_handlers(self, mock_builder, mock_env_vars):
        """Test that main() registers the correct handlers."""
        mock_app = MagicMock()
        mock_builder_instance = MagicMock()
        mock_builder_instance.token.return_value = mock_builder_instance
        mock_builder_instance.build.return_value = mock_app
        mock_builder.return_value = mock_builder_instance

        halt.main()

        # Get all handler calls
        handler_calls = mock_app.add_handler.call_args_list

        # Verify CommandHandler for "halt" was added
        assert len(handler_calls) >= 1
