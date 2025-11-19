"""
Unit tests for halt.py module.
"""
import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock, patch, call
import os
import sys

# Add parent directory to path to import halt module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import halt
from telegram.error import TimedOut
import httpcore


class TestShutdownMachine:
    """Test cases for shutdown_machine() function."""

    def test_shutdown_windows(self, mock_subprocess_run, mock_platform_system):
        """Test shutdown command on Windows."""
        mock_platform_system('Windows')
        
        halt.shutdown_machine()
        
        assert mock_subprocess_run.called
        call_args = mock_subprocess_run.call_args
        assert call_args[0][0] == ["shutdown", "/s", "/f", "/t", "0"]

    def test_shutdown_linux(self, mock_subprocess_run, mock_platform_system):
        """Test shutdown command on Linux."""
        mock_platform_system('Linux')
        
        halt.shutdown_machine()
        
        assert mock_subprocess_run.called
        call_args = mock_subprocess_run.call_args
        assert call_args[0][0] == ["sudo", "shutdown", "now"]

    def test_shutdown_darwin(self, mock_subprocess_run, mock_platform_system):
        """Test shutdown command on macOS (Darwin)."""
        mock_platform_system('Darwin')
        
        halt.shutdown_machine()
        
        assert mock_subprocess_run.called
        call_args = mock_subprocess_run.call_args
        assert call_args[0][0] == ["sudo", "shutdown", "now"]


class TestHaltCommand:
    """Test cases for the halt() command handler."""

    @pytest.mark.asyncio
    async def test_halt_no_args(self, mock_telegram_update, mock_telegram_context, 
                                 mock_subprocess_run, mock_platform_node):
        """Test /halt command with no arguments."""
        mock_telegram_context.args = []
        
        await halt.halt(mock_telegram_update, mock_telegram_context)
        
        # Verify reply was sent
        assert mock_telegram_update.message.reply_text.called
        reply_text = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Shutting down all machines" in reply_text
        
        # Verify shutdown was called
        assert mock_subprocess_run.called

    @pytest.mark.asyncio
    async def test_halt_with_matching_device(self, mock_telegram_update, mock_telegram_context,
                                             mock_subprocess_run, mock_platform_node):
        """Test /halt command with matching device name."""
        mock_telegram_context.args = ['test-device']
        
        await halt.halt(mock_telegram_update, mock_telegram_context)
        
        # Verify reply was sent
        assert mock_telegram_update.message.reply_text.called
        reply_text = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Shutting down test-device" in reply_text
        
        # Verify shutdown was called
        assert mock_subprocess_run.called

    @pytest.mark.asyncio
    async def test_halt_with_non_matching_device(self, mock_telegram_update, mock_telegram_context,
                                                  mock_subprocess_run, mock_platform_node):
        """Test /halt command with non-matching device name."""
        mock_telegram_context.args = ['other-device']
        
        await halt.halt(mock_telegram_update, mock_telegram_context)
        
        # Verify reply was sent
        assert mock_telegram_update.message.reply_text.called
        reply_text = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "does not match" in reply_text
        
        # Verify shutdown was NOT called
        assert not mock_subprocess_run.called

    @pytest.mark.asyncio
    async def test_halt_with_multiple_args(self, mock_telegram_update, mock_telegram_context,
                                           mock_subprocess_run):
        """Test /halt command with multiple arguments (invalid usage)."""
        mock_telegram_context.args = ['arg1', 'arg2']
        
        await halt.halt(mock_telegram_update, mock_telegram_context)
        
        # Verify usage message was sent
        assert mock_telegram_update.message.reply_text.called
        reply_text = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Usage: /halt [DEVICENAME]" in reply_text
        
        # Verify shutdown was NOT called
        assert not mock_subprocess_run.called


class TestErrorHandler:
    """Test cases for the error_handler() function."""

    @pytest.mark.asyncio
    async def test_error_handler_timed_out(self, mock_telegram_update, mock_telegram_context,
                                           mock_subprocess_run, mock_platform_node):
        """Test error handler with TimedOut exception."""
        mock_telegram_context.error = TimedOut("Connection timeout")
        mock_telegram_context.args = []
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            await halt.error_handler(mock_telegram_update, mock_telegram_context)
            
            # Verify sleep was called
            mock_sleep.assert_called_once_with(5)
            
            # Verify halt was called after retry
            assert mock_telegram_update.message.reply_text.called

    @pytest.mark.asyncio
    async def test_error_handler_connect_timeout(self, mock_telegram_update, mock_telegram_context,
                                                  mock_subprocess_run, mock_platform_node):
        """Test error handler with httpcore.ConnectTimeout exception."""
        mock_telegram_context.error = httpcore.ConnectTimeout("Connection timeout")
        mock_telegram_context.args = []
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            await halt.error_handler(mock_telegram_update, mock_telegram_context)
            
            # Verify sleep was called
            mock_sleep.assert_called_once_with(5)
            
            # Verify halt was called after retry
            assert mock_telegram_update.message.reply_text.called

    @pytest.mark.asyncio
    async def test_error_handler_other_exception(self, mock_telegram_update, mock_telegram_context):
        """Test error handler with other exception types."""
        mock_telegram_context.error = ValueError("Some other error")
        
        # Should raise the exception
        with pytest.raises(ValueError):
            await halt.error_handler(mock_telegram_update, mock_telegram_context)


class TestSendFunctionInHalt:
    """Test cases for the send() function in halt.py."""

    def test_send_success(self, mock_env_vars, mock_requests_post):
        """Test successful message sending from halt module."""
        message = "Test message"
        result = halt.send(message)
        
        # Verify requests.post was called
        assert mock_requests_post.called
        call_args = mock_requests_post.call_args
        
        # Verify URL construction
        expected_url = f"https://api.telegram.org/bot{mock_env_vars['BOT_TOKEN']}/sendMessage"
        assert call_args[0][0] == expected_url
        
        # Verify data payload
        assert call_args[1]['data']['chat_id'] == mock_env_vars['CHAT_ID']
        assert call_args[1]['data']['text'] == message
        
        # Verify return value
        assert result == {'ok': True, 'result': {'message_id': 1}}


class TestMainFunction:
    """Test cases for the main() function."""

    @patch('halt.ApplicationBuilder')
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
        mock_builder_instance.token.assert_called_once_with(mock_env_vars['BOT_TOKEN'])
        mock_builder_instance.build.assert_called_once()
        
        # Verify handlers were added
        assert mock_app.add_handler.called
        assert mock_app.add_error_handler.called
        
        # Verify polling was started
        mock_app.run_polling.assert_called_once()

    @patch('halt.ApplicationBuilder')
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
        # Check that a CommandHandler was added (we can't easily check the command name without inspecting the handler)

