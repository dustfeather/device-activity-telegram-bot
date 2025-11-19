"""Send Telegram notification on device login."""
import asyncio
import platform

from .telegram_client import send_message


async def main() -> None:
    """Main entry point for send script."""
    device_name = platform.node()  # Get the device name
    message = f"Your device '{device_name}' has been logged into."
    await send_message(message)


if __name__ == "__main__":
    asyncio.run(main())
