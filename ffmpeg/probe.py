"""
ffmpeg/probe.py

Media probe utilities used by the processing engine.
"""

from __future__ import annotations

from pathlib import Path

from helpers.ffprobe import ffprobe


class MediaProbe:
    """High-level media information."""

    @staticmethod
    async def get_info(file: str | Path) -> dict:

        file = Path(file)

        width, height = await ffprobe.resolution(file)

        return {
            "path": str(file),
            "name": file.name,
            "extension": file.suffix.lower(),
            "duration": await ffprobe.duration(file),
            "size": await ffprobe.size(file),
            "bitrate": await ffprobe.bitrate(file),
            "codec": await ffprobe.codec(file),
            "fps": await ffprobe.fps(file),
            "width": width,
            "height": height,
            "has_video": await ffprobe.has_video(file),
            "has_audio": await ffprobe.has_audio(file),
            "streams": await ffprobe.streams(file),
            "format": await ffprobe.format(file),
        }

    @staticmethod
    async def available_qualities(
        file: str | Path,
    ) -> list[int]:
        """
        Returns only the valid output qualities.
        Example:
        1080 -> [1080,720,480,360,240,144]
        720 -> [720,480,360,240,144]
        """

        _, height = await ffprobe.resolution(file)

        qualities = [
            2160,
            1440,
            1080,
            720,
            480,
            360,
            240,
            144,
        ]

        return [
            q
            for q in qualities
            if q <= height
        ]

    @staticmethod
    async def is_video(
        file: str | Path,
    ) -> bool:

        return await ffprobe.has_video(file)

    @staticmethod
    async def is_audio(
        file: str | Path,
    ) -> bool:

        return await ffprobe.has_audio(file)

    @staticmethod
    async def duration(
        file: str | Path,
    ) -> float:

        return await ffprobe.duration(file)

    @staticmethod
    async def resolution(
        file: str | Path,
    ) -> tuple[int, int]:

        return await ffprobe.resolution(file)

    @staticmethod
    async def codec(
        file: str | Path,
    ) -> str | None:

        return await ffprobe.codec(file)

    @staticmethod
    async def bitrate(
        file: str | Path,
    ) -> int:

        return await ffprobe.bitrate(file)

    @staticmethod
    async def size(
        file: str | Path,
    ) -> int:

        return await ffprobe.size(file)


probe = MediaProbe()
