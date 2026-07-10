"""
web.py

Health check web server for Render, Railway, Koyeb, Docker, and VPS.
"""

from __future__ import annotations

import asyncio
from contextlib import suppress

from aiohttp import web

from config import config
from logger import get_logger

log = get_logger(__name__)


class WebServer:
    """Minimal async web server for health checks."""

    def __init__(self) -> None:
        self._app = web.Application()
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None

        self._app.router.add_get("/", self.index)
        self._app.router.add_get("/health", self.health)
        self._app.router.add_get("/ping", self.ping)

    async def index(self, request: web.Request) -> web.Response:
        return web.json_response(
            {
                "status": "running",
                "service": "AniToon Bot",
                "version": "1.0.0",
            }
        )

    async def health(self, request: web.Request) -> web.Response:
        return web.json_response(
            {
                "status": "healthy",
            }
        )

    async def ping(self, request: web.Request) -> web.Response:
        return web.Response(text="pong")

    async def start(self) -> None:
        """Start HTTP server."""

        if self._runner:
            return

        self._runner = web.AppRunner(self._app)
        await self._runner.setup()

        self._site = web.TCPSite(
            self._runner,
            host=config.HOST,
            port=config.PORT,
        )

        await self._site.start()

        log.info(
            "Web server started on http://%s:%s",
            config.HOST,
            config.PORT,
        )

    async def stop(self) -> None:
        """Stop HTTP server."""

        if self._runner:
            with suppress(Exception):
                await self._runner.cleanup()

            self._runner = None
            self._site = None

            log.info("Web server stopped.")


web_server = WebServer()


async def keep_alive() -> None:
    """
    Keep the process alive forever.
    Used together with other asyncio tasks.
    """

    while True:
        await asyncio.sleep(3600)
