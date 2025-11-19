import os
import platform
import subprocess
import logging
import asyncio
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from dotenv import load_dotenv
from telegram.error import TimedOut
import httpcore
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from .env file
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# Get the bot token from the .env file
bot_token = os.getenv('BOT_TOKEN')

if not bot_token:
    logger.error("No BOT_TOKEN found in environment variables.")
else:
    # Mask token in logs to prevent log injection and token exposure
    # Sanitize by removing any control characters that could be used for log injection
    masked_token = f"{bot_token[:4]}...{bot_token[-4:]}" if len(bot_token) > 8 else "****"
    # Remove control characters (newlines, carriage returns, etc.) to prevent log injection
    masked_token = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', masked_token)
    logger.info("Bot token loaded: %s", masked_token)

# Get the OS name
os_name = platform.node()

# Define the shutdown command based on the OS
def shutdown_machine():
    if platform.system() == 'Windows':
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
    elif platform.system() == 'Linux' or platform.system() == 'Darwin':  # Darwin for macOS
        subprocess.run(["sudo", "shutdown", "now"])

# Define the command handler for /halt
async def halt(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text('Shutting down all machines...')
        shutdown_machine()
    elif len(context.args) == 1:
        device_name = context.args[0]
        # Sanitize device name to prevent injection attacks
        # Only allow alphanumeric, hyphen, underscore, and dot characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', device_name):
            await update.message.reply_text('Invalid device name format.')
            return
        
        if device_name == os_name:
            await update.message.reply_text(f'Shutting down {device_name}...')
            shutdown_machine()
        else:
            await update.message.reply_text(f'Device name {device_name} does not match any machine.')
    else:
        await update.message.reply_text('Usage: /halt [DEVICENAME]')

async def error_handler(update: Update, context: CallbackContext) -> None:
    try:
        raise context.error
    except (TimedOut, httpcore.ConnectTimeout):
        logger.warning('Request timed out. Retrying in 5 seconds...')
        await asyncio.sleep(5)
        await halt(update, context)

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

def main():
    # Create the Application using ApplicationBuilder
    application = ApplicationBuilder().token(bot_token).build()

    # Register the /halt command handler
    application.add_handler(CommandHandler("halt", halt))

    # Register the error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    device_name = platform.node()  # Get the device name
    message = f"'{device_name}' started halt monitor."
    send(message)
    main()
