"""Telegram bot for remote device shutdown."""

import asyncio
import logging
import platform
import re
import subprocess

import httpcore
from telegram import Update
from telegram.error import TimedOut
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

from .config import settings
from .telegram_client import send_message

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the OS name
os_name = platform.node()


def shutdown_machine() -> None:
    """Shutdown the machine based on the operating system."""
    system = platform.system()
    if system == "Windows":
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"], check=False)
    elif system in ("Linux", "Darwin"):  # Darwin for macOS
        subprocess.run(["sudo", "shutdown", "now"], check=False)
    else:
        logger.warning(f"Unsupported operating system: {system}")


async def halt(update: Update, context: CallbackContext) -> None:
    """Handle the /halt command."""
    if not update.message:
        return

    args = context.args or []
    if len(args) == 0:
        await update.message.reply_text("Shutting down all machines...")
        shutdown_machine()
    elif len(args) == 1:
        device_name = args[0]
        # Sanitize device name to prevent injection attacks
        # Only allow alphanumeric, hyphen, underscore, and dot characters
        if not re.match(r"^[a-zA-Z0-9._-]+$", device_name):
            await update.message.reply_text("Invalid device name format.")
            return

        if device_name == os_name:
            await update.message.reply_text(f"Shutting down {device_name}...")
            shutdown_machine()
        else:
            await update.message.reply_text(
                f"Device name {device_name} does not match any machine."
            )
    else:
        await update.message.reply_text("Usage: /halt [DEVICENAME]")


async def error_handler(update: Update, context: CallbackContext) -> None:
    """Handle errors in the bot."""
    if not context.error:
        return

    try:
        raise context.error
    except (TimedOut, httpcore.ConnectTimeout):
        logger.warning("Request timed out. Retrying in 5 seconds...")
        await asyncio.sleep(5)
        if update:
            await halt(update, context)


def main() -> None:
    """Main entry point for halt bot."""
    # Create the Application using ApplicationBuilder
    application = ApplicationBuilder().token(settings.bot_token).build()

    # Register the /halt command handler
    application.add_handler(CommandHandler("halt", halt))

    # Register the error handler
    application.add_error_handler(error_handler)  # type: ignore[arg-type]

    # Start the Bot
    application.run_polling()


async def startup_notification() -> None:
    """Send startup notification."""
    device_name = platform.node()  # Get the device name
    message = f"'{device_name}' started halt monitor."
    await send_message(message)


if __name__ == "__main__":
    asyncio.run(startup_notification())
    main()
