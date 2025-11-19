"""
Unit tests for send.py module.
"""
import pytest
from unittest.mock import patch, Mock
import os
import sys
import platform

# Add parent directory to path to import send module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import send


class TestSendFunction:
    """Test cases for the send() function."""

    def test_send_success(self, mock_env_vars, mock_requests_post):
        """Test successful message sending."""
        message = "Test message"
        result = send.send(message)
        
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

    def test_send_with_empty_message(self, mock_env_vars, mock_requests_post):
        """Test sending an empty message."""
        message = ""
        result = send.send(message)
        
        assert mock_requests_post.called
        call_args = mock_requests_post.call_args
        assert call_args[1]['data']['text'] == ""

    def test_send_uses_env_vars(self, mock_env_vars, mock_requests_post):
        """Test that send() correctly uses environment variables."""
        message = "Test"
        send.send(message)
        
        call_args = mock_requests_post.call_args
        expected_url = f"https://api.telegram.org/bot{mock_env_vars['BOT_TOKEN']}/sendMessage"
        assert call_args[0][0] == expected_url
        assert call_args[1]['data']['chat_id'] == mock_env_vars['CHAT_ID']

    def test_send_http_error(self, mock_env_vars, mock_requests_post):
        """Test handling of HTTP errors."""
        # Mock a failed response
        mock_response = Mock()
        mock_response.json.return_value = {'ok': False, 'error_code': 400}
        mock_requests_post.return_value = mock_response
        
        result = send.send("Test message")
        
        assert result == {'ok': False, 'error_code': 400}

    @patch('platform.node')
    def test_main_execution(self, mock_node, mock_env_vars, mock_requests_post):
        """Test the main execution block of send.py."""
        mock_node.return_value = 'test-device'
        
        # Test main block logic directly without using exec() to avoid code injection
        # Simulate what happens in the __main__ block
        device_name = platform.node()
        message = f"Your device '{device_name}' has been logged into."
        send.send(message)
        
        # Verify send was called with correct message
        assert mock_requests_post.called
        call_args = mock_requests_post.call_args
        assert "test-device" in call_args[1]['data']['text']
        assert "logged into" in call_args[1]['data']['text']

