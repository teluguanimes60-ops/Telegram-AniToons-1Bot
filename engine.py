"""
engine.py

Main processing engine.

Part 1
"""

from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path

from pyrogram import Client
from pyrogram.types import Message

from database.queue import queue_db
from logger import get_logger
from queue.state import queue_state
from utils.paths import (
    create_job_directory,
    cleanup_job_directory,
)

log = get_logger(__name__)


class ProcessingEngine:
    """
    Main processing engine.

    Executes one queue job from start to finish.
    """

    def __init__(self, client: Client) -> None:

        self.client = client

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    async def process(
        self,
        job_id: str,
        message: Message,
    ) -> None:
        """
        Process one queued job.
        """

        state = queue_state.create(job_id)

        await queue_db.start_job(job_id)

        work_dir = create_job_directory(job_id)

        try:

            await self._run(
                job_id=job_id,
                message=message,
                work_dir=work_dir,
            )

            await queue_db.finish_job(job_id)

        except asyncio.CancelledError:

            await queue_db.cancel_job(job_id)

            raise

        except Exception as e:

            log.exception(
                "Job %s failed",
                job_id,
            )

            await queue_db.fail_job(
                job_id,
                str(e),
            )

            raise

        finally:

            queue_state.remove(job_id)

            with contextlib.suppress(Exception):
                cleanup_job_directory(work_dir)

    # --------------------------------------------------
    # Internal Pipeline
    # --------------------------------------------------

    async def _run(
        self,
        job_id: str,
        message: Message,
        work_dir: Path,
    ) -> None:

        await self._check_pause_cancel(job_id)

        await queue_db.set_step(
            job_id,
            "Preparing..."
        )

        log.info(
            "Processing job %s",
            job_id,
        )

        # Part 2 begins here.

    # --------------------------------------------------
    # Pause / Cancel
    # --------------------------------------------------

    async def _check_pause_cancel(
        self,
        job_id: str,
    ) -> None:

        await queue_state.wait_if_paused(job_id)

        if queue_state.is_cancelled(job_id):
            raise asyncio.CancelledError

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    async def update_progress(
        self,
        job_id: str,
        percent: float,
        step: str,
    ) -> None:

        queue_state.set_progress(
            job_id,
            percent,
        )

        queue_state.set_step(
            job_id,
            step,
        )

        await queue_db.set_progress(
            job_id,
            percent,
        )

        await queue_db.set_step(
            job_id,
            step,
        )

      # --------------------------------------------------
    # Main Processing Pipeline
    # --------------------------------------------------

    async def _run(
        self,
        job_id: str,
        message: Message,
        work_dir: Path,
    ) -> None:

        from downloader.telegram import TelegramDownloader
        from uploader.telegram import TelegramUploader
        from ffmpeg.processor import FFmpegProcessor
        from helpers.rename import RenameHelper
        from helpers.thumbnail import ThumbnailHelper

        downloader = TelegramDownloader(self.client)
        uploader = TelegramUploader(self.client)
        ffmpeg = FFmpegProcessor()
        rename = RenameHelper()
        thumbnail = ThumbnailHelper()

        # ---------------------------------------------
        # Step 1 : Download
        # ---------------------------------------------

        await self.update_progress(
            job_id,
            0,
            "Downloading..."
        )

        downloaded = await downloader.download(
            message=message,
            output_dir=work_dir,
            progress_callback=lambda p: self.update_progress(
                job_id,
                p * 0.25,
                "Downloading..."
            ),
            pause_callback=lambda: self._check_pause_cancel(job_id),
        )

        await self._check_pause_cancel(job_id)

        # ---------------------------------------------
        # Step 2 : Rename
        # ---------------------------------------------

        await self.update_progress(
            job_id,
            30,
            "Preparing filename..."
        )

        output_name = await rename.generate_filename(
            message=message,
            original_path=downloaded,
        )

        output_file = work_dir / output_name

        downloaded.rename(output_file)

        await queue_db.set_filename(
            job_id,
            output_name,
        )

        await self._check_pause_cancel(job_id)

        # ---------------------------------------------
        # Step 3 : Thumbnail
        # ---------------------------------------------

        await self.update_progress(
            job_id,
            40,
            "Preparing thumbnail..."
        )

        thumb = await thumbnail.get_thumbnail(
            message=message,
            media_path=output_file,
        )

        await self._check_pause_cancel(job_id)

        # ---------------------------------------------
        # Step 4 : Processing
        # ---------------------------------------------

        settings = await ffmpeg.load_user_settings(
            message.from_user.id
        )

        processed = output_file

        if settings.requires_processing:

            await self.update_progress(
                job_id,
                45,
                "Processing media..."
            )

            processed = await ffmpeg.process(
                input_file=output_file,
                output_dir=work_dir,
                settings=settings,
                progress_callback=lambda p: self.update_progress(
                    job_id,
                    45 + (p * 0.35),
                    "Processing..."
                ),
                pause_callback=lambda: self._check_pause_cancel(job_id),
            )

        await self._check_pause_cancel(job_id)

        # ---------------------------------------------
        # Step 5 : Upload
        # ---------------------------------------------

        await self.update_progress(
            job_id,
            82,
            "Uploading..."
        )

        await uploader.upload(
            original_message=message,
            file=processed,
            thumbnail=thumb,
            progress_callback=lambda p: self.update_progress(
                job_id,
                82 + (p * 0.18),
                "Uploading..."
            ),
            pause_callback=lambda: self._check_pause_cancel(job_id),
        )

        # ---------------------------------------------
        # Finish
        # ---------------------------------------------

        await self.update_progress(
            job_id,
            100,
            "Completed"
        )

        log.info(
            "Finished processing %s",
            job_id,
        )

      # --------------------------------------------------
    # Instant Edit Mode
    # --------------------------------------------------

    async def _instant_edit(
        self,
        job_id: str,
        message: Message,
    ) -> bool:
        """
        Rename a Telegram file without downloading or
        re-uploading it. Returns True if handled.
        """

        from database.settings import settings_db
        from helpers.rename import RenameHelper

        mode = await settings_db.get_mode(message.from_user.id)

        if mode != "instant_edit":
            return False

        rename = RenameHelper()

        filename = await rename.generate_filename(
            message=message,
            original_path=None,
        )

        await self.client.edit_message_media(
            chat_id=message.chat.id,
            message_id=message.id,
            media=message.media.value,
            file_name=filename,
        )

        await queue_db.set_filename(job_id, filename)
        await self.update_progress(job_id, 100, "Instant Edit Complete")

        return True

    # --------------------------------------------------
    # Media Detection
    # --------------------------------------------------

    async def detect_media_type(
        self,
        message: Message,
    ) -> str:

        if message.video:
            return "video"

        if message.document:
            return "document"

        if message.audio:
            return "audio"

        if message.photo:
            return "photo"

        if message.animation:
            return "animation"

        if message.voice:
            return "voice"

        if message.video_note:
            return "video_note"

        return "unknown"

    # --------------------------------------------------
    # Temporary Cleanup
    # --------------------------------------------------

    async def cleanup(
        self,
        work_dir: Path,
    ) -> None:

        with contextlib.suppress(Exception):
            cleanup_job_directory(work_dir)

    # --------------------------------------------------
    # Retry Helper
    # --------------------------------------------------

    async def retry(
        self,
        coro,
        retries: int = 3,
    ):

        last_error = None

        for _ in range(retries):

            try:
                return await coro()

            except Exception as e:

                last_error = e

                await asyncio.sleep(2)

        raise last_error

    # --------------------------------------------------
    # Processing Statistics
    # --------------------------------------------------

    async def save_statistics(
        self,
        user_id: int,
        mode: str,
    ) -> None:

        from database.statistics import statistics_db

        await statistics_db.increment_total_jobs()

        await statistics_db.increment_user_jobs(user_id)

        await statistics_db.increment_mode(mode)

    # --------------------------------------------------
    # Supported Media
    # --------------------------------------------------

    SUPPORTED_MEDIA = {
        "video",
        "document",
        "audio",
        "photo",
        "animation",
        "voice",
        "video_note",
    }
