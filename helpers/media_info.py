"""
helpers/media_info.py

Media information helper for AniToons Bot.
"""

from __future__ import annotations

from pathlib import Path

from helpers.ffprobe import ffprobe


class MediaInfo:

    @staticmethod
    async def get(file: str | Path) -> dict:
        """
        Returns complete media information.
        """

        file = Path(file)

        width, height = await ffprobe.resolution(file)
        duration = await ffprobe.duration(file)
        bitrate = await ffprobe.bitrate(file)
        codec = await ffprobe.codec(file)
        size = await ffprobe.size(file)

        return {
            "filename": file.name,
            "extension": file.suffix.lower(),
            "size": size,
            "duration": duration,
            "codec": codec,
            "bitrate": bitrate,
            "width": width,
            "height": height,
            "resolution": (
                f"{width}x{height}"
                if width and height
                else "Unknown"
            ),
            "has_video": await ffprobe.has_video(file),
            "has_audio": await ffprobe.has_audio(file),
        }

    @staticmethod
    async def text(file: str | Path) -> str:
        """
        Returns formatted media information.
        """

        info = await MediaInfo.get(file)

        lines = [
            "📄 <b>Media Information</b>",
            "",
            f"📁 <b>Name:</b> {info['filename']}",
            f"🗂 <b>Extension:</b> {info['extension']}",
            f"📦 <b>Size:</b> {info['size']} bytes",
            f"🎬 <b>Resolution:</b> {info['resolution']}",
            f"🎞 <b>Codec:</b> {info['codec'] or 'Unknown'}",
            f"⏱ <b>Duration:</b> {round(info['duration'], 2)} sec",
            f"📡 <b>Bitrate:</b> {info['bitrate']} bps",
            f"🎥 <b>Video:</b> {'Yes' if info['has_video'] else 'No'}",
            f"🎵 <b>Audio:</b> {'Yes' if info['has_audio'] else 'No'}",
        ]

        return "\n".join(lines)


media_info = MediaInfo()
