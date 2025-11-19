import requests
from dotenv import load_dotenv
import os
import platform
import sys
import re
from urllib.parse import quote

# Load environment variables from .env file
load_dotenv()

def send(message):
    token = os.getenv('BOT_TOKEN')  # Fetch the bot token from the .env file
    chat_id = os.getenv('CHAT_ID')  # Fetch the chat ID from the .env file
    
    # Validate token and chat_id to prevent SSRF
    if not token or not chat_id:
        raise ValueError("BOT_TOKEN and CHAT_ID must be set")
    
    # Validate token format to prevent SSRF - Telegram bot tokens are numeric:alphanumeric
    # Format: digits:alphanumeric (e.g., "123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    if not re.match(r'^[0-9]+:[A-Za-z0-9_-]+$', token):
        raise ValueError("Invalid BOT_TOKEN format")
    
    # Validate chat_id is numeric or alphanumeric (can be negative for groups)
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
    response = requests.post(url, data=data, timeout=10)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    device_name = platform.node()  # Get the device name
    message = f"Your device '{device_name}' has been logged into."
    send(message)
