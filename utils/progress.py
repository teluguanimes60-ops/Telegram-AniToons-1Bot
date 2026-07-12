"""
utils/progress.py

Unified progress manager.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, Message

from logger import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class ProgressData:
    stage: str
    current: int
    total: int
    speed: float
    eta: float
    elapsed: float
    filename: str

    @property
    def percent(self) -> float:
        if self.total <= 0:
            return 0.0

        return min(
            100.0,
            self.current * 100 / self.total,
        )


class ProgressManager:

    EDIT_INTERVAL = 2

    def __init__(self):

        self._last_edit: dict[int, float] = {}

    # ------------------------------------------
    # Progress Bar
    # ------------------------------------------

    @staticmethod
    def progress_bar(
        percent: float,
        length: int = 20,
    ) -> str:

        filled = int(
            percent / 100 * length
        )

        return (
            "█" * filled
            + "░" * (length - filled)
        )

    # ------------------------------------------
    # Human Size
    # ------------------------------------------

    @staticmethod
    def human_size(
        size: float,
    ) -> str:

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

    # ------------------------------------------
    # Human Time
    # ------------------------------------------

    @staticmethod
    def human_time(
        seconds: float,
    ) -> str:

        seconds = int(seconds)

        h, seconds = divmod(seconds, 3600)

        m, s = divmod(seconds, 60)

        if h:

            return f"{h:02}:{m:02}:{s:02}"

        return f"{m:02}:{s:02}"

    # ------------------------------------------
    # Message
    # ------------------------------------------

    def build_text(
        self,
        data: ProgressData,
    ) -> str:

        return (
            f"**{data.stage}**\n\n"
            f"`{data.filename}`\n\n"
            f"{self.progress_bar(data.percent)}\n"
            f"**{data.percent:.1f}%**\n\n"
            f"Transferred : "
            f"{self.human_size(data.current)} / "
            f"{self.human_size(data.total)}\n"
            f"Speed : {self.human_size(data.speed)}/s\n"
            f"ETA : {self.human_time(data.eta)}\n"
            f"Elapsed : {self.human_time(data.elapsed)}"
        )

    # ------------------------------------------
    # Edit
    # ------------------------------------------

    async def update(
        self,
        message: Message,
        data: ProgressData,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:

        now = time.monotonic()

        last = self._last_edit.get(
            message.id,
            0,
        )

        if now - last < self.EDIT_INTERVAL:
            return

        self._last_edit[message.id] = now

        try:

            await message.edit_text(
                self.build_text(data),
                reply_markup=reply_markup,
            )

        except FloodWait as e:

            await asyncio.sleep(e.value)

        except Exception:

            log.exception(
                "Progress update failed."
            )


progress_manager = ProgressManager()

# --------------------------------------------------
# System Information
# --------------------------------------------------

import psutil

class ProgressManager:

    # --------------------------------------------------
    # CPU
    # --------------------------------------------------

    @staticmethod
    def cpu_usage() -> str:

        return f"{psutil.cpu_percent():.0f}%"

    # --------------------------------------------------
    # RAM
    # --------------------------------------------------

    @staticmethod
    def ram_usage() -> str:

        return f"{psutil.virtual_memory().percent:.0f}%"

    # --------------------------------------------------
    # Download Template
    # --------------------------------------------------

    def download_text(
        self,
        data: ProgressData,
    ) -> str:

        return (
            f"📥 **Downloading**\n\n"
            f"`{data.filename}`\n\n"
            f"{self.progress_bar(data.percent)}\n"
            f"**{data.percent:.1f}%**\n\n"
            f"Downloaded : "
            f"{self.human_size(data.current)} / "
            f"{self.human_size(data.total)}\n"
            f"Speed : {self.human_size(data.speed)}/s\n"
            f"ETA : {self.human_time(data.eta)}\n"
            f"Elapsed : {self.human_time(data.elapsed)}\n"
            f"CPU : {self.cpu_usage()}\n"
            f"RAM : {self.ram_usage()}"
        )

    # --------------------------------------------------
    # Processing Template
    # --------------------------------------------------

    def processing_text(
        self,
        data: ProgressData,
    ) -> str:

        return (
            f"⚙️ **Processing**\n\n"
            f"`{data.filename}`\n\n"
            f"{self.progress_bar(data.percent)}\n"
            f"**{data.percent:.1f}%**\n\n"
            f"Speed : {data.speed:.2f}x\n"
            f"ETA : {self.human_time(data.eta)}\n"
            f"Elapsed : {self.human_time(data.elapsed)}\n"
            f"CPU : {self.cpu_usage()}\n"
            f"RAM : {self.ram_usage()}"
        )

    # --------------------------------------------------
    # Upload Template
    # --------------------------------------------------

    def upload_text(
        self,
        data: ProgressData,
    ) -> str:

        return (
            f"📤 **Uploading**\n\n"
            f"`{data.filename}`\n\n"
            f"{self.progress_bar(data.percent)}\n"
            f"**{data.percent:.1f}%**\n\n"
            f"Uploaded : "
            f"{self.human_size(data.current)} / "
            f"{self.human_size(data.total)}\n"
            f"Speed : {self.human_size(data.speed)}/s\n"
            f"ETA : {self.human_time(data.eta)}\n"
            f"Elapsed : {self.human_time(data.elapsed)}\n"
            f"CPU : {self.cpu_usage()}\n"
            f"RAM : {self.ram_usage()}"
        )

    # --------------------------------------------------
    # Queue Template
    # --------------------------------------------------

    def queue_text(
        self,
        position: int,
        total: int,
    ) -> str:

        return (
            "⏳ **Queued**\n\n"
            f"Position : **{position}**\n"
            f"Waiting : **{total}** jobs"
        )

    # --------------------------------------------------
    # Status Text
    # --------------------------------------------------

    def render(
        self,
        data: ProgressData,
    ) -> str:

        stage = data.stage.lower()

        if stage == "download":
            return self.download_text(data)

        if stage == "upload":
            return self.upload_text(data)

        if stage == "processing":
            return self.processing_text(data)

        return self.build_text(data)

    # --------------------------------------------------
    # Safe Update
    # --------------------------------------------------

    async def safe_update(
        self,
        message: Message,
        data: ProgressData,
        reply_markup=None,
    ):

        try:

            await self.update(
                message,
                data,
                reply_markup,
            )

        except Exception:

            log.exception(
                "Progress update failed."
            )

    # --------------------------------------------------
    # Cleanup Cache
    # --------------------------------------------------

    def cleanup(
        self,
        message_id: int,
    ):

        self._last_edit.pop(
            message_id,
            None,
        )
