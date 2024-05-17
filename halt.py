import os
import platform
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the .env file
bot_token = os.getenv('BOT_TOKEN')

# Get the OS name
os_name = platform.node()

# Define the shutdown command based on the OS
def shutdown_machine():
    if platform.system() == 'Windows':
        subprocess.run(["shutdown", "/s", "/t", "0"])
    elif platform.system() == 'Linux' or platform.system() == 'Darwin':  # Darwin for macOS
        subprocess.run(["sudo", "shutdown", "now"])

# Define the command handler for /halt
def halt(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text('Usage: /halt <DEVICENAME>')
        return

    device_name = context.args[0]
    if device_name == os_name:
        update.message.reply_text(f'Shutting down {device_name}...')
        shutdown_machine()
    else:
        update.message.reply_text(f'Device name {device_name} does not match this machine.')

def main():
    # Create the Updater and pass it your bot's token
    updater = Updater(token=bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the /halt command handler
    dispatcher.add_handler(CommandHandler("halt", halt))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
