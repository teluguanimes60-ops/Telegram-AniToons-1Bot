"""
helpers/caption.py

Caption builder and formatter for AniToons Bot.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


class CaptionHelper:
    """Creates captions from user templates."""

    DEFAULT_CAPTION = (
        "{filename}\n"
        "📦 Size : {size}\n"
        "🎬 Quality : {quality}\n"
        "⏱ Duration : {duration}"
    )

    # --------------------------------------------------
    # Human Size
    # --------------------------------------------------

    @staticmethod
    def human_size(size: int) -> str:

        units = ["B", "KB", "MB", "GB", "TB"]

        value = float(size)

        index = 0

        while value >= 1024 and index < len(units) - 1:
            value /= 1024
            index += 1

        return f"{value:.2f} {units[index]}"

    # --------------------------------------------------
    # Human Time
    # --------------------------------------------------

    @staticmethod
    def human_duration(seconds: int | float) -> str:

        seconds = int(seconds)

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours:
            return f"{hours:02}:{minutes:02}:{secs:02}"

        return f"{minutes:02}:{secs:02}"

    # --------------------------------------------------
    # Variables
    # --------------------------------------------------

    def variables(
        self,
        *,
        filename: str,
        size: int = 0,
        quality: str = "-",
        duration: int = 0,
        username: str = "",
    ) -> dict:

        return {
            "filename": filename,
            "name": Path(filename).stem,
            "extension": Path(filename).suffix,
            "size": self.human_size(size),
            "quality": quality,
            "duration": self.human_duration(duration),
            "username": username,
            "date": datetime.now().strftime("%d-%m-%Y"),
            "time": datetime.now().strftime("%H:%M"),
        }

    # --------------------------------------------------
    # Build Caption
    # --------------------------------------------------

    def build(
        self,
        template: str | None,
        *,
        filename: str,
        size: int = 0,
        quality: str = "-",
        duration: int = 0,
        username: str = "",
    ) -> str:

        if not template:
            template = self.DEFAULT_CAPTION

        data = self.variables(
            filename=filename,
            size=size,
            quality=quality,
            duration=duration,
            username=username,
        )

        try:
            return template.format(**data)

        except Exception:
            return self.DEFAULT_CAPTION.format(**data)

    # --------------------------------------------------
    # Preview
    # --------------------------------------------------

    def preview(
        self,
        template: str,
    ) -> str:

        return self.build(
            template,
            filename="Example Video.mkv",
            size=734003200,
            quality="1080p",
            duration=1530,
            username="AniToons",
        )


caption_helper = CaptionHelper()
