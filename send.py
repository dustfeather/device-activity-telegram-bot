import requests
from dotenv import load_dotenv
import os
import platform
import sys

def load_env():
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        bundle_dir = sys._MEIPASS
        env_path = os.path.join(bundle_dir, '.env')
    else:
        # Running in normal Python environment
        env_path = os.path.join(os.path.dirname(__file__), '.env')

    load_dotenv(env_path)

def send(message):
    token = os.getenv('BOT_TOKEN')  # Fetch the bot token from the .env file
    chat_id = os.getenv('CHAT_ID')  # Fetch the chat ID from the .env file
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=data)
    return response.json()

if __name__ == "__main__":
    load_env()
    device_name = platform.node()  # Get the device name
    message = f"Your PC '{device_name}' has been logged into."
    send(message)
