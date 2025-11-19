"""Telegram API client for sending messages."""
import re
from typing import Any
from urllib.parse import quote

import httpx

from .config import settings


async def send_message(message: str) -> dict[str, Any]:
    """
    Send a message via Telegram Bot API.
    
    Args:
        message: The message text to send.
        
    Returns:
        The JSON response from the Telegram API.
        
    Raises:
        ValueError: If BOT_TOKEN or CHAT_ID are invalid or missing.
        httpx.HTTPStatusError: If the HTTP request fails.
    """
    token = settings.bot_token
    chat_id = settings.chat_id
    
    # Validate token format to prevent SSRF - Telegram bot tokens are numeric:alphanumeric
    # Format: digits:alphanumeric (e.g., "123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    if not re.match(r'^[0-9]+:[A-Za-z0-9_-]+$', token):
        raise ValueError("Invalid BOT_TOKEN format")
    
    # Validate chat_id is numeric (can be negative for groups)
    if not re.match(r'^-?[0-9]+$', str(chat_id)):
        raise ValueError("Invalid CHAT_ID format")
    
    # Construct URL with proper encoding to prevent SSRF
    telegram_api_base = "https://api.telegram.org"
    # URL-encode the token to prevent injection of path separators or query parameters
    # Preserve colon (:) as it's required in Telegram bot token format
    encoded_token = quote(token, safe=':')
    url = f"{telegram_api_base}/bot{encoded_token}/sendMessage"
    
    # Validate URL starts with expected domain (double-check after encoding)
    if not url.startswith(telegram_api_base):
        raise ValueError("Invalid URL constructed")
    
    data = {
        'chat_id': chat_id,
        'text': message
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, data=data)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result
