import requests
from dotenv import load_dotenv
import os
import platform
import sys

# Load environment variables from .env file
load_dotenv()

def send(message):
    token = os.getenv('BOT_TOKEN')  # Fetch the bot token from the .env file
    chat_id = os.getenv('CHAT_ID')  # Fetch the chat ID from the .env file
    
    # Validate token and chat_id to prevent SSRF
    if not token or not chat_id:
        raise ValueError("BOT_TOKEN and CHAT_ID must be set")
    
    # Construct URL with validation - only allow Telegram API domain
    telegram_api_base = "https://api.telegram.org"
    url = f"{telegram_api_base}/bot{token}/sendMessage"
    
    # Validate URL starts with expected domain
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
