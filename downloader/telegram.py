"""
downloader/telegram.py

Async Telegram downloader.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Awaitable, Callable

from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from logger import get_logger

log = get_logger(__name__)

ProgressCallback = Callable[[float], Awaitable[None]]
PauseCallback = Callable[[], Awaitable[None]]


class TelegramDownloader:
    """
    Telegram file downloader with:

    • Progress callback
    • Pause / Resume
    • Cancel support
    • Retry
    • FloodWait handling
    """

    MAX_RETRIES = 3

    def __init__(self, client: Client) -> None:
        self.client = client

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    async def download(
        self,
        message: Message,
        output_dir: Path,
        progress_callback: ProgressCallback | None = None,
        pause_callback: PauseCallback | None = None,
    ) -> Path:

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        media = self._get_media(message)

        filename = self._filename(media)

        destination = output_dir / filename

        await self._download_with_retry(
            message=message,
            destination=destination,
            progress_callback=progress_callback,
            pause_callback=pause_callback,
        )

        return destination

    # --------------------------------------------------
    # Retry Wrapper
    # --------------------------------------------------

    async def _download_with_retry(
        self,
        message: Message,
        destination: Path,
        progress_callback: ProgressCallback | None,
        pause_callback: PauseCallback | None,
    ) -> None:

        last_error = None

        for attempt in range(self.MAX_RETRIES):

            try:

                await message.download(
                    file_name=str(destination),
                    progress=self._progress,
                    progress_args=(
                        progress_callback,
                        pause_callback,
                    ),
                )

                return

            except FloodWait as e:

                log.warning(
                    "FloodWait %s sec",
                    e.value,
                )

                await asyncio.sleep(e.value)

            except Exception as e:

                last_error = e

                log.exception(
                    "Download attempt %d failed.",
                    attempt + 1,
                )

                await asyncio.sleep(2)

        raise last_error

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    async def _progress(
        self,
        current: int,
        total: int,
        progress_callback: ProgressCallback | None,
        pause_callback: PauseCallback | None,
    ) -> None:

        if pause_callback:
            await pause_callback()

        if progress_callback:

            percent = (
                current / total * 100
                if total
                else 0
            )

            await progress_callback(percent)

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _get_media(message: Message):

        return (
            message.document
            or message.video
            or message.audio
            or message.animation
            or message.photo
            or message.voice
            or message.video_note
        )

    @staticmethod
    def _filename(media) -> str:

        if hasattr(media, "file_name"):

            if media.file_name:
                return media.file_name

        return f"{media.file_unique_id}.bin"

          # --------------------------------------------------
    # Download Information
    # --------------------------------------------------

    async def get_file_size(
        self,
        message: Message,
    ) -> int:

        media = self._get_media(message)

        return getattr(
            media,
            "file_size",
            0,
        )

    async def get_filename(
        self,
        message: Message,
    ) -> str:

        media = self._get_media(message)

        return self._filename(media)

    # --------------------------------------------------
    # Progress Wrapper
    # --------------------------------------------------

    async def progress_wrapper(
        self,
        current: int,
        total: int,
        started_at: float,
        progress_callback: ProgressCallback | None,
        pause_callback: PauseCallback | None,
    ) -> None:

        if pause_callback:
            await pause_callback()

        now = asyncio.get_running_loop().time()

        elapsed = max(
            now - started_at,
            0.001,
        )

        speed = current / elapsed

        eta = (
            (total - current) / speed
            if speed > 0
            else 0
        )

        percent = (
            current / total * 100
            if total
            else 0
        )

        if progress_callback:

            await progress_callback(
                percent,
            )

        self._last_speed = speed
        self._last_eta = eta

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    @property
    def last_speed(self) -> float:
        """
        Bytes per second.
        """

        return getattr(
            self,
            "_last_speed",
            0.0,
        )

    @property
    def last_eta(self) -> float:
        """
        Seconds remaining.
        """

        return getattr(
            self,
            "_last_eta",
            0.0,
        )

    # --------------------------------------------------
    # Verification
    # --------------------------------------------------

    async def verify_download(
        self,
        path: Path,
    ) -> bool:

        return (
            path.exists()
            and path.is_file()
            and path.stat().st_size > 0
        )

    # --------------------------------------------------
    # Safe Download
    # --------------------------------------------------

    async def safe_download(
        self,
        message: Message,
        output_dir: Path,
        progress_callback: ProgressCallback | None = None,
        pause_callback: PauseCallback | None = None,
    ) -> Path:

        path = await self.download(
            message,
            output_dir,
            progress_callback,
            pause_callback,
        )

        if not await self.verify_download(path):

            raise RuntimeError(
                "Downloaded file verification failed."
            )

        return path

    # --------------------------------------------------
    # Supported Media
    # --------------------------------------------------

    @staticmethod
    def supported(
        message: Message,
    ) -> bool:

        return TelegramDownloader._get_media(
            message
        ) is not None

  """
downloader/telegram.py

Part 3
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from time import monotonic


# --------------------------------------------------
# Progress Information
# --------------------------------------------------

@dataclass(slots=True)
class ProgressInfo:
    current: int
    total: int
    percent: float
    speed: float
    eta: float
    elapsed: float


# --------------------------------------------------
# Progress Generator
# --------------------------------------------------

    async def build_progress(
        self,
        current: int,
        total: int,
        started: float,
    ) -> ProgressInfo:

        elapsed = max(
            monotonic() - started,
            0.001,
        )

        speed = current / elapsed

        eta = (
            (total - current) / speed
            if speed > 0
            else 0
        )

        percent = (
            current * 100 / total
            if total
            else 0
        )

        return ProgressInfo(
            current=current,
            total=total,
            percent=percent,
            speed=speed,
            eta=eta,
            elapsed=elapsed,
        )


# --------------------------------------------------
# Cleanup
# --------------------------------------------------

    async def cleanup(
        self,
        path: Path,
    ) -> None:

        try:

            if path.exists():
                path.unlink()

        except Exception:

            log.exception(
                "Failed removing %s",
                path,
            )


# --------------------------------------------------
# Wait Helper
# --------------------------------------------------

    async def wait(
        self,
        seconds: float,
    ) -> None:

        await asyncio.sleep(seconds)


# --------------------------------------------------
# Download Size
# --------------------------------------------------

    async def readable_size(
        self,
        message: Message,
    ) -> str:

        size = await self.get_file_size(message)

        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB",
        ]

        index = 0

        while size >= 1024 and index < len(units) - 1:

            size /= 1024

            index += 1

        return f"{size:.2f} {units[index]}"


# --------------------------------------------------
# Retry Delay
# --------------------------------------------------

    async def retry_delay(
        self,
        attempt: int,
    ) -> None:

        delay = min(
            2 ** attempt,
            15,
        )

        await asyncio.sleep(delay)


# --------------------------------------------------
# Validation
# --------------------------------------------------

    async def validate_message(
        self,
        message: Message,
    ) -> None:

        if not self.supported(message):

            raise ValueError(
                "Unsupported Telegram media."
            )


# --------------------------------------------------
# Download Wrapper
# --------------------------------------------------

    async def download_file(
        self,
        message: Message,
        output_dir: Path,
        progress_callback=None,
        pause_callback=None,
    ) -> Path:

        await self.validate_message(message)

        return await self.safe_download(
            message,
            output_dir,
            progress_callback,
            pause_callback,
        )


# --------------------------------------------------
# Information
# --------------------------------------------------

    async def info(
        self,
        message: Message,
    ) -> dict:

        media = self._get_media(message)

        return {
            "file_name": self._filename(media),
            "file_size": getattr(
                media,
                "file_size",
                0,
            ),
            "mime_type": getattr(
                media,
                "mime_type",
                "",
            ),
            "unique_id": getattr(
                media,
                "file_unique_id",
                "",
            ),
        }
