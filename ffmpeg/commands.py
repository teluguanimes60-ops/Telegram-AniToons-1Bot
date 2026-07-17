"""
ffmpeg/commands.py

FFmpeg command builder for AniToons Bot.
"""

from __future__ import annotations

from pathlib import Path


class FFmpegCommands:
    """Build FFmpeg command arguments."""

    @staticmethod
    def convert_format(
        input_file: str | Path,
        output_file: str | Path,
    ) -> list[str]:

        return [
            "ffmpeg",
            "-y",
            "-i",
            str(input_file),
            "-map",
            "0",
            "-c",
            "copy",
            str(output_file),
        ]

    @staticmethod
    def convert_quality(
        input_file: str | Path,
        output_file: str | Path,
        height: int,
    ) -> list[str]:

        return [
            "ffmpeg",
            "-y",
            "-i",
            str(input_file),
            "-vf",
            f"scale=-2:{height}",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output_file),
        ]

    @staticmethod
    def compress(
        input_file: str | Path,
        output_file: str | Path,
        crf: int = 28,
    ) -> list[str]:

        return [
            "ffmpeg",
            "-y",
            "-i",
            str(input_file),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            str(crf),
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(output_file),
        ]

    @staticmethod
    def extract_audio(
        input_file: str | Path,
        output_file: str | Path,
    ) -> list[str]:

        return [
            "ffmpeg",
            "-y",
            "-i",
            str(input_file),
            "-vn",
            "-acodec",
            "libmp3lame",
            "-q:a",
            "2",
            str(output_file),
        ]

    @staticmethod
    def generate_thumbnail(
        input_file: str | Path,
        output_file: str | Path,
        timestamp: str = "00:00:01",
    ) -> list[str]:

        return [
            "ffmpeg",
            "-y",
            "-ss",
            timestamp,
            "-i",
            str(input_file),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output_file),
        ]

    @staticmethod
    def gif(
        input_file: str | Path,
        output_file: str | Path,
        fps: int = 12,
        width: int = 480,
    ) -> list[str]:

        return [
            "ffmpeg",
            "-y",
            "-i",
            str(input_file),
            "-vf",
            f"fps={fps},scale={width}:-1:flags=lanczos",
            str(output_file),
        ]

    @staticmethod
    def watermark(
        input_file: str | Path,
        logo_file: str | Path,
        output_file: str | Path,
    ) -> list[str]:

        return [
            "ffmpeg",
            "-y",
            "-i",
            str(input_file),
            "-i",
            str(logo_file),
            "-filter_complex",
            "overlay=W-w-20:H-h-20",
            "-codec:a",
            "copy",
            str(output_file),
        ]


commands = FFmpegCommands()
