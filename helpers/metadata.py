"""
helpers/metadata.py

Media metadata helper.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path


class MetadataHelper:
    """Read media metadata using FFprobe."""

    def __init__(self) -> None:
        self.ffprobe = "ffprobe"

    # --------------------------------------------------
    # Probe
    # --------------------------------------------------

    async def probe(
        self,
        file: str | Path,
    ) -> dict:

        file = Path(file)

        cmd = [
            self.ffprobe,
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

    async def get_format(
        self,
        file: str | Path,
    ) -> dict:

        data = await self.probe(file)

        return data.get("format", {})

    # --------------------------------------------------
    # Streams
    # --------------------------------------------------

    async def get_streams(
        self,
        file: str | Path,
    ) -> list:

        data = await self.probe(file)

        return data.get("streams", [])

    # --------------------------------------------------
    # Video Stream
    # --------------------------------------------------

    async def get_video_stream(
        self,
        file: str | Path,
    ) -> dict | None:

        streams = await self.get_streams(file)

        for stream in streams:

            if stream.get("codec_type") == "video":
                return stream

        return None

    # --------------------------------------------------
    # Audio Stream
    # --------------------------------------------------

    async def get_audio_stream(
        self,
        file: str | Path,
    ) -> dict | None:

        streams = await self.get_streams(file)

        for stream in streams:

            if stream.get("codec_type") == "audio":
                return stream

        return None

    # --------------------------------------------------
    # Resolution
    # --------------------------------------------------

    async def resolution(
        self,
        file: str | Path,
    ) -> tuple[int, int]:

        stream = await self.get_video_stream(file)

        if stream is None:
            return (0, 0)

        return (
            int(stream.get("width", 0)),
            int(stream.get("height", 0)),
        )

    # --------------------------------------------------
    # Duration
    # --------------------------------------------------

    async def duration(
        self,
        file: str | Path,
    ) -> float:

        info = await self.get_format(file)

        return float(
            info.get("duration", 0)
        )

    # --------------------------------------------------
    # Size
    # --------------------------------------------------

    async def size(
        self,
        file: str | Path,
    ) -> int:

        info = await self.get_format(file)

        return int(
            info.get("size", 0)
        )

    # --------------------------------------------------
    # Bitrate
    # --------------------------------------------------

    async def bitrate(
        self,
        file: str | Path,
    ) -> int:

        info = await self.get_format(file)

        return int(
            info.get("bit_rate", 0)
        )

    # --------------------------------------------------
    # Codec
    # --------------------------------------------------

    async def codec(
        self,
        file: str | Path,
    ) -> str | None:

        stream = await self.get_video_stream(file)

        if stream is None:
            return None

        return stream.get("codec_name")

    # --------------------------------------------------
    # FPS
    # --------------------------------------------------

    async def fps(
        self,
        file: str | Path,
    ) -> float:

        stream = await self.get_video_stream(file)

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


metadata_helper = MetadataHelper()
