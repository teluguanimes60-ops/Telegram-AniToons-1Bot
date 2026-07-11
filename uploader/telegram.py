"""
uploader/telegram.py

Telegram uploader.

Part 1
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


class TelegramUploader:

    MAX_RETRIES = 3

    def __init__(
        self,
        client: Client,
    ) -> None:

        self.client = client

    # --------------------------------------------------
    # Upload
    # --------------------------------------------------

    async def upload(
        self,
        original_message: Message,
        file: Path,
        thumbnail: Path | None = None,
        caption: str | None = None,
        progress_callback: ProgressCallback | None = None,
        pause_callback: PauseCallback | None = None,
    ):

        if caption is None:
            caption = file.name

        suffix = file.suffix.lower()

        if suffix in {
            ".mp4",
            ".mkv",
            ".mov",
            ".webm",
            ".avi",
        }:

            return await self.upload_video(
                original_message,
                file,
                thumbnail,
                caption,
                progress_callback,
                pause_callback,
            )

        if suffix in {
            ".mp3",
            ".aac",
            ".flac",
            ".wav",
            ".ogg",
        }:

            return await self.upload_audio(
                original_message,
                file,
                thumbnail,
                caption,
                progress_callback,
                pause_callback,
            )

        return await self.upload_document(
            original_message,
            file,
            thumbnail,
            caption,
            progress_callback,
            pause_callback,
        )

    # --------------------------------------------------
    # Document
    # --------------------------------------------------

    async def upload_document(

        self,
        original_message: Message,
        file: Path,
        thumbnail: Path | None,
        caption: str,
        progress_callback,
        pause_callback,

    ):

        return await self._retry(

            lambda: self.client.send_document(

                chat_id=original_message.chat.id,

                document=str(file),

                thumb=str(thumbnail) if thumbnail else None,

                caption=caption,

                progress=self._progress,

                progress_args=(

                    progress_callback,

                    pause_callback,

                ),

            )

        )

    # --------------------------------------------------
    # Video
    # --------------------------------------------------

    async def upload_video(

        self,

        original_message: Message,

        file: Path,

        thumbnail: Path | None,

        caption: str,

        progress_callback,

        pause_callback,

    ):

        return await self._retry(

            lambda: self.client.send_video(

                chat_id=original_message.chat.id,

                video=str(file),

                thumb=str(thumbnail) if thumbnail else None,

                caption=caption,

                supports_streaming=True,

                progress=self._progress,

                progress_args=(

                    progress_callback,

                    pause_callback,

                ),

            )

        )

    # --------------------------------------------------
    # Audio
    # --------------------------------------------------

    async def upload_audio(

        self,

        original_message: Message,

        file: Path,

        thumbnail: Path | None,

        caption: str,

        progress_callback,

        pause_callback,

    ):

        return await self._retry(

            lambda: self.client.send_audio(

                chat_id=original_message.chat.id,

                audio=str(file),

                thumb=str(thumbnail) if thumbnail else None,

                caption=caption,

                progress=self._progress,

                progress_args=(

                    progress_callback,

                    pause_callback,

                ),

            )

        )

    # --------------------------------------------------
    # Retry
    # --------------------------------------------------

    async def _retry(self, func):

        last = None

        for attempt in range(self.MAX_RETRIES):

            try:

                return await func()

            except FloodWait as e:

                log.warning(

                    "FloodWait %s",

                    e.value,

                )

                await asyncio.sleep(e.value)

            except Exception as e:

                last = e

                log.exception(

                    "Upload failed (%d)",

                    attempt + 1,

                )

                await asyncio.sleep(2)

        raise last

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    async def _progress(

        self,

        current,

        total,

        progress_callback,

        pause_callback,

    ):

        if pause_callback:

            await pause_callback()

        if progress_callback:

            percent = (

                current * 100 / total

                if total

                else 0

            )

            await progress_callback(percent)

          # --------------------------------------------------
    # Photo
    # --------------------------------------------------

    async def upload_photo(
        self,
        original_message: Message,
        file: Path,
        caption: str,
        progress_callback=None,
        pause_callback=None,
    ):

        return await self._retry(
            lambda: self.client.send_photo(
                chat_id=original_message.chat.id,
                photo=str(file),
                caption=caption,
                progress=self._progress,
                progress_args=(
                    progress_callback,
                    pause_callback,
                ),
            )
        )

    # --------------------------------------------------
    # Animation
    # --------------------------------------------------

    async def upload_animation(
        self,
        original_message: Message,
        file: Path,
        caption: str,
        progress_callback=None,
        pause_callback=None,
    ):

        return await self._retry(
            lambda: self.client.send_animation(
                chat_id=original_message.chat.id,
                animation=str(file),
                caption=caption,
                progress=self._progress,
                progress_args=(
                    progress_callback,
                    pause_callback,
                ),
            )
        )

    # --------------------------------------------------
    # Voice
    # --------------------------------------------------

    async def upload_voice(
        self,
        original_message: Message,
        file: Path,
        caption: str = "",
        progress_callback=None,
        pause_callback=None,
    ):

        return await self._retry(
            lambda: self.client.send_voice(
                chat_id=original_message.chat.id,
                voice=str(file),
                caption=caption,
                progress=self._progress,
                progress_args=(
                    progress_callback,
                    pause_callback,
                ),
            )
        )

    # --------------------------------------------------
    # Video Note
    # --------------------------------------------------

    async def upload_video_note(
        self,
        original_message: Message,
        file: Path,
        progress_callback=None,
        pause_callback=None,
    ):

        return await self._retry(
            lambda: self.client.send_video_note(
                chat_id=original_message.chat.id,
                video_note=str(file),
                progress=self._progress,
                progress_args=(
                    progress_callback,
                    pause_callback,
                ),
            )
        )

    # --------------------------------------------------
    # Upload Statistics
    # --------------------------------------------------

    async def file_size(
        self,
        file: Path,
    ) -> int:

        return file.stat().st_size

    async def readable_size(
        self,
        file: Path,
    ) -> str:

        size = await self.file_size(file)

        units = ["B", "KB", "MB", "GB", "TB"]

        index = 0

        while size >= 1024 and index < len(units) - 1:

            size /= 1024

            index += 1

        return f"{size:.2f} {units[index]}"

    # --------------------------------------------------
    # File Validation
    # --------------------------------------------------

    async def validate_file(
        self,
        file: Path,
    ) -> None:

        if not file.exists():

            raise FileNotFoundError(file)

        if not file.is_file():

            raise ValueError(
                "Invalid upload target."
            )

        if file.stat().st_size == 0:

            raise ValueError(
                "Empty file."
            )

    # --------------------------------------------------
    # Upload Metadata
    # --------------------------------------------------

    async def info(
        self,
        file: Path,
    ) -> dict:

        await self.validate_file(file)

        return {
            "name": file.name,
            "suffix": file.suffix,
            "size": await self.file_size(file),
            "human_size": await self.readable_size(file),
        }

    # --------------------------------------------------
    # Upload Speed
    # --------------------------------------------------

    @property
    def last_speed(self):

        return getattr(
            self,
            "_last_speed",
            0.0,
        )

    @property
    def last_eta(self):

        return getattr(
            self,
            "_last_eta",
            0.0,
        )

  """
uploader/telegram.py

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
class UploadProgress:
    current: int
    total: int
    percent: float
    speed: float
    eta: float
    elapsed: float


class TelegramUploader:

    # --------------------------------------------------
    # Progress Builder
    # --------------------------------------------------

    async def build_progress(
        self,
        current: int,
        total: int,
        started: float,
    ) -> UploadProgress:

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

        self._last_speed = speed
        self._last_eta = eta

        return UploadProgress(
            current=current,
            total=total,
            percent=percent,
            speed=speed,
            eta=eta,
            elapsed=elapsed,
        )

    # --------------------------------------------------
    # Upload Wrapper
    # --------------------------------------------------

    async def upload_file(
        self,
        original_message: Message,
        file: Path,
        thumbnail: Path | None = None,
        caption: str | None = None,
        progress_callback=None,
        pause_callback=None,
    ):

        await self.validate_file(file)

        return await self.upload(
            original_message=original_message,
            file=file,
            thumbnail=thumbnail,
            caption=caption,
            progress_callback=progress_callback,
            pause_callback=pause_callback,
        )

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    async def cleanup(
        self,
        file: Path,
        thumbnail: Path | None = None,
    ) -> None:

        try:

            if file.exists():
                file.unlink()

        except Exception:

            log.exception(
                "Failed removing %s",
                file,
            )

        if thumbnail:

            try:

                if thumbnail.exists():
                    thumbnail.unlink()

            except Exception:

                log.exception(
                    "Failed removing %s",
                    thumbnail,
                )

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
    # Upload Type
    # --------------------------------------------------

    def detect_upload_type(
        self,
        file: Path,
    ) -> str:

        suffix = file.suffix.lower()

        if suffix in {
            ".mp4",
            ".mkv",
            ".avi",
            ".mov",
            ".webm",
        }:
            return "video"

        if suffix in {
            ".mp3",
            ".aac",
            ".wav",
            ".ogg",
            ".flac",
        }:
            return "audio"

        if suffix in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:
            return "photo"

        if suffix == ".gif":
            return "animation"

        return "document"

    # --------------------------------------------------
    # Upload Summary
    # --------------------------------------------------

    async def summary(
        self,
        file: Path,
    ) -> dict:

        info = await self.info(file)

        return {
            **info,
            "speed": self.last_speed,
            "eta": self.last_eta,
        }

    # --------------------------------------------------
    # Cancel Check
    # --------------------------------------------------

    async def check_cancel(
        self,
        pause_callback,
    ) -> None:

        if pause_callback:
            await pause_callback()

    # --------------------------------------------------
    # Production Log
    # --------------------------------------------------

    async def log_upload(
        self,
        file: Path,
    ) -> None:

        log.info(
            "Uploaded %s (%s)",
            file.name,
            await self.readable_size(file),
        )
