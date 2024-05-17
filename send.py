import requests
from dotenv import load_dotenv
import os
import platform

# Load environment variables from .env file
load_dotenv()

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
    device_name = platform.node()  # Get the device name
    message = f"Your PC '{device_name}' has been logged into."
    send(message)
