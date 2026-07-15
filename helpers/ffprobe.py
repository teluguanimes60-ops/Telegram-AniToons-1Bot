"""
helpers/ffprobe.py

Reusable FFprobe helper for AniToons Bot.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from logger import get_logger

log = get_logger(__name__)


class FFprobe:

    def __init__(self) -> None:
        self.binary = "ffprobe"

    # --------------------------------------------------
    # Execute
    # --------------------------------------------------

    async def run(
        self,
        file: str | Path,
    ) -> dict[str, Any]:

        file = Path(file)

        cmd = [
            self.binary,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(file),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(
                stderr.decode(errors="ignore")
            )

        return json.loads(stdout)

    # --------------------------------------------------
    # Format
    # --------------------------------------------------

    async def format(
        self,
        file: str | Path,
    ) -> dict:

        data = await self.run(file)

        return data.get("format", {})

    # --------------------------------------------------
    # Streams
    # --------------------------------------------------

    async def streams(
        self,
        file: str | Path,
    ) -> list:

        data = await self.run(file)

        return data.get("streams", [])

    # --------------------------------------------------
    # Video Stream
    # --------------------------------------------------

    async def video(
        self,
        file: str | Path,
    ) -> dict | None:

        for stream in await self.streams(file):

            if stream.get("codec_type") == "video":
                return stream

        return None

    # --------------------------------------------------
    # Audio Stream
    # --------------------------------------------------

    async def audio(
        self,
        file: str | Path,
    ) -> dict | None:

        for stream in await self.streams(file):

            if stream.get("codec_type") == "audio":
                return stream

        return None

    # --------------------------------------------------
    # Subtitle Streams
    # --------------------------------------------------

    async def subtitles(
        self,
        file: str | Path,
    ) -> list:

        result = []

        for stream in await self.streams(file):

            if stream.get("codec_type") == "subtitle":
                result.append(stream)

        return result

    # --------------------------------------------------
    # Resolution
    # --------------------------------------------------

    async def resolution(
        self,
        file: str | Path,
    ) -> tuple[int, int]:

        video = await self.video(file)

        if video is None:
            return (0, 0)

        return (
            int(video.get("width", 0)),
            int(video.get("height", 0)),
        )

    # --------------------------------------------------
    # Duration
    # --------------------------------------------------

    async def duration(
        self,
        file: str | Path,
    ) -> float:

        info = await self.format(file)

        return float(info.get("duration", 0))

    # --------------------------------------------------
    # Size
    # --------------------------------------------------

    async def size(
        self,
        file: str | Path,
    ) -> int:

        info = await self.format(file)

        return int(info.get("size", 0))

    # --------------------------------------------------
    # Bitrate
    # --------------------------------------------------

    async def bitrate(
        self,
        file: str | Path,
    ) -> int:

        info = await self.format(file)

        return int(info.get("bit_rate", 0))

    # --------------------------------------------------
    # Codec
    # --------------------------------------------------

    async def codec(
        self,
        file: str | Path,
    ) -> str | None:

        stream = await self.video(file)

        if stream is None:
            return None

        return stream.get("codec_name")

    # --------------------------------------------------
    # Frame Rate
    # --------------------------------------------------

    async def fps(
        self,
        file: str | Path,
    ) -> float:

        stream = await self.video(file)

        if stream is None:
            return 0.0

        rate = stream.get(
            "r_frame_rate",
            "0/1",
        )

        try:
            num, den = rate.split("/")
            return float(num) / float(den)
        except Exception:
            return 0.0

    # --------------------------------------------------
    # Has Audio
    # --------------------------------------------------

    async def has_audio(
        self,
        file: str | Path,
    ) -> bool:

        return await self.audio(file) is not None

    # --------------------------------------------------
    # Has Video
    # --------------------------------------------------

    async def has_video(
        self,
        file: str | Path,
    ) -> bool:

        return await self.video(file) is not None


ffprobe = FFprobe()
