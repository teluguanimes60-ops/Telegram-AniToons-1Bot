"""
main.py

Application entry point.
"""

from __future__ import annotations

import asyncio
import signal
from contextlib import suppress

from bot import bot
from database import db
from logger import get_logger, setup_logger
from web import keep_alive, web_server

log = get_logger(__name__)


class AniToonApplication:
    """Main application controller."""

    def __init__(self) -> None:
        self.shutdown_event = asyncio.Event()

    async def startup(self) -> None:
        """Initialize all services."""

        setup_logger()

        log.info("=" * 60)
        log.info("Starting AniToon Bot...")
        log.info("=" * 60)

        # Database
        await db.connect()

        # Web Server
        await web_server.start()

        # Telegram Bot
        await bot.start()

        me = await bot.get_me()

        log.info("Bot Started Successfully")
        log.info("Bot Name : %s", me.first_name)
        log.info("Bot Username : @%s", me.username)
        log.info("Bot ID : %s", me.id)

    async def shutdown(self) -> None:
        """Gracefully stop all services."""

        log.info("Stopping AniToon Bot...")

        with suppress(Exception):
            await bot.stop()

        with suppress(Exception):
            await web_server.stop()

        with suppress(Exception):
            await db.disconnect()

        log.info("Shutdown Complete.")

    async def run(self) -> None:
        """Run application."""

        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            with suppress(NotImplementedError):
                loop.add_signal_handler(
                    sig,
                    self.shutdown_event.set,
                )

        try:
            await self.startup()

            await asyncio.gather(
                keep_alive(),
                self.shutdown_event.wait(),
            )

        finally:
            await self.shutdown()


async def main() -> None:
    app = AniToonApplication()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
