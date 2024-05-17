import os
import platform
import subprocess
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from dotenv import load_dotenv
from telegram.error import TimedOut
import httpcore

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
    logger.info(f"Bot token loaded: {bot_token}")

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
        await update.message.reply_text(f'Shutting down all machines...')
        shutdown_machine()
    elif len(context.args) == 1:
        device_name = context.args[0]
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
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=data)
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
