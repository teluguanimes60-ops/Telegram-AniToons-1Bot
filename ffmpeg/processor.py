"""
ffmpeg/processor.py

FFmpeg Processing Engine

Part 1
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from logger import get_logger
from database.settings import settings_db

log = get_logger(__name__)


@dataclass(slots=True)
class ProcessorSettings:
    """
    Runtime processing settings.
    """

    quality: str | None = None
    output_format: str | None = None
    compression: str | None = None
    extract_audio: bool = False
    remove_metadata: bool = False
    preserve_subtitles: bool = True

    @property
    def requires_processing(self) -> bool:

        return any(
            [
                self.quality,
                self.output_format,
                self.compression,
                self.extract_audio,
                self.remove_metadata,
            ]
        )


class FFmpegProcessor:

    def __init__(self) -> None:

        self.ffmpeg = "ffmpeg"

        self.ffprobe = "ffprobe"

    # --------------------------------------------------
    # User Settings
    # --------------------------------------------------

    async def load_user_settings(
        self,
        user_id: int,
    ) -> ProcessorSettings:

        settings = await settings_db.get_user_settings(
            user_id
        )

        return ProcessorSettings(
            quality=settings.get("quality"),
            output_format=settings.get("format"),
            compression=settings.get("compression"),
            extract_audio=settings.get(
                "extract_audio",
                False,
            ),
            remove_metadata=settings.get(
                "remove_metadata",
                False,
            ),
            preserve_subtitles=settings.get(
                "preserve_subtitles",
                True,
            ),
        )

    # --------------------------------------------------
    # FFprobe
    # --------------------------------------------------

    async def probe(
        self,
        media: Path,
    ) -> dict[str, Any]:

        cmd = [
            self.ffprobe,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(media),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:

            raise RuntimeError(
                stderr.decode()
            )

        return json.loads(stdout)

    # --------------------------------------------------
    # Video Stream
    # --------------------------------------------------

    async def video_stream(
        self,
        media: Path,
    ) -> dict | None:

        info = await self.probe(media)

        for stream in info["streams"]:

            if stream.get("codec_type") == "video":

                return stream

        return None

    # --------------------------------------------------
    # Audio Stream
    # --------------------------------------------------

    async def audio_stream(
        self,
        media: Path,
    ) -> dict | None:

        info = await self.probe(media)

        for stream in info["streams"]:

            if stream.get("codec_type") == "audio":

                return stream

        return None

    # --------------------------------------------------
    # Resolution
    # --------------------------------------------------

    async def resolution(
        self,
        media: Path,
    ) -> tuple[int, int]:

        video = await self.video_stream(
            media
        )

        if video is None:

            return (0, 0)

        return (
            int(video["width"]),
            int(video["height"]),
        )

    # --------------------------------------------------
    # Duration
    # --------------------------------------------------

    async def duration(
        self,
        media: Path,
    ) -> float:

        info = await self.probe(media)

        return float(
            info["format"].get(
                "duration",
                0,
            )
        )

    # --------------------------------------------------
    # Bitrate
    # --------------------------------------------------

    async def bitrate(
        self,
        media: Path,
    ) -> int:

        info = await self.probe(media)

        return int(
            info["format"].get(
                "bit_rate",
                0,
            )
        )

  """
ffmpeg/processor.py

Part 2
"""

from __future__ import annotations

import asyncio
from pathlib import Path


class FFmpegProcessor:

    # --------------------------------------------------
    # Resolution Scale
    # --------------------------------------------------

    QUALITY_MAP = {
        "2160": 2160,
        "1440": 1440,
        "1080": 1080,
        "720": 720,
        "480": 480,
        "360": 360,
        "240": 240,
        "144": 144,
    }

    async def scale_filter(
        self,
        input_file: Path,
        quality: str,
    ) -> list[str]:

        width, height = await self.resolution(input_file)

        if height == 0:
            return []

        target = self.QUALITY_MAP.get(
            str(quality),
            height,
        )

        target = min(target, height)

        return [
            "-vf",
            f"scale=-2:{target}",
        ]

    # --------------------------------------------------
    # Compression
    # --------------------------------------------------

    COMPRESSION = {
        "low": 23,
        "medium": 26,
        "high": 30,
        "extreme": 34,
    }

    async def compression_args(
        self,
        level: str | None,
    ) -> list[str]:

        if not level:
            return []

        crf = self.COMPRESSION.get(
            level.lower(),
            23,
        )

        return [
            "-crf",
            str(crf),
        ]

    # --------------------------------------------------
    # Audio Extraction
    # --------------------------------------------------

    async def audio_extract_args(
        self,
        output: Path,
    ) -> tuple[Path, list[str]]:

        audio_file = output.with_suffix(".mp3")

        args = [
            "-vn",
            "-acodec",
            "libmp3lame",
            "-ab",
            "320k",
        ]

        return audio_file, args

    # --------------------------------------------------
    # Format Conversion
    # --------------------------------------------------

    async def output_path(
        self,
        input_file: Path,
        output_dir: Path,
        fmt: str | None,
    ) -> Path:

        if not fmt:
            return output_dir / input_file.name

        fmt = fmt.lower().replace(".", "")

        return output_dir / f"{input_file.stem}.{fmt}"

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    async def metadata_args(
        self,
        remove: bool,
    ) -> list[str]:

        if not remove:
            return []

        return [
            "-map_metadata",
            "-1",
        ]

    # --------------------------------------------------
    # Subtitle Handling
    # --------------------------------------------------

    async def subtitle_args(
        self,
        preserve: bool,
    ) -> list[str]:

        if preserve:
            return [
                "-map",
                "0",
            ]

        return [
            "-sn",
        ]

    # --------------------------------------------------
    # Build Command
    # --------------------------------------------------

    async def build_command(
        self,
        input_file: Path,
        output_dir: Path,
        settings: ProcessorSettings,
    ) -> tuple[Path, list[str]]:

        output = await self.output_path(
            input_file,
            output_dir,
            settings.output_format,
        )

        command = [
            self.ffmpeg,
            "-y",
            "-i",
            str(input_file),
        ]

        command.extend(
            await self.scale_filter(
                input_file,
                settings.quality or "",
            )
        )

        command.extend(
            await self.compression_args(
                settings.compression,
            )
        )

        command.extend(
            await self.metadata_args(
                settings.remove_metadata,
            )
        )

        command.extend(
            await self.subtitle_args(
                settings.preserve_subtitles,
            )
        )

        if settings.extract_audio:

            output, args = await self.audio_extract_args(
                output
            )

            command.extend(args)

        command.append(str(output))

        return output, command

    # --------------------------------------------------
    # Execute FFmpeg
    # --------------------------------------------------

    async def execute(
        self,
        command: list[str],
    ) -> None:

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:

            raise RuntimeError(
                stderr.decode(
                    errors="ignore",
                )
            )

"""
ffmpeg/processor.py

Part 3
"""

from __future__ import annotations

import asyncio
import re
import time
from pathlib import Path


class FFmpegProcessor:

    # --------------------------------------------------
    # Parse FFmpeg Progress
    # --------------------------------------------------

    async def parse_progress(
        self,
        line: str,
        duration: float,
    ) -> dict:

        match = re.search(
            r"time=(\d+):(\d+):(\d+\.\d+)",
            line,
        )

        if not match:

            return {
                "percent": 0,
                "speed": 0,
                "eta": 0,
            }

        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))

        current = (
            hours * 3600
            + minutes * 60
            + seconds
        )

        percent = (
            current * 100 / duration
            if duration
            else 0
        )

        speed_match = re.search(
            r"speed=(\d+\.?\d*)x",
            line,
        )

        speed = 0

        if speed_match:
            speed = float(
                speed_match.group(1)
            )

        remaining = (
            duration - current
        )

        eta = (
            remaining / speed
            if speed > 0
            else 0
        )

        return {
            "percent": min(
                percent,
                100,
            ),
            "speed": speed,
            "eta": eta,
        }

    # --------------------------------------------------
    # Execute With Progress
    # --------------------------------------------------

    async def execute_with_progress(
        self,
        command: list[str],
        duration: float,
        progress_callback=None,
        pause_callback=None,
    ):

        process = await asyncio.create_subprocess_exec(
            *command,
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.DEVNULL,
        )

        started = time.time()

        while True:

            line = await process.stderr.readline()

            if not line:
                break

            decoded = line.decode(
                errors="ignore"
            )

            if pause_callback:

                await pause_callback()

            data = await self.parse_progress(
                decoded,
                duration,
            )

            if progress_callback:

                await progress_callback(
                    data
                )

        result = await process.wait()

        if result != 0:

            raise RuntimeError(
                "FFmpeg processing failed."
            )

        return True

    # --------------------------------------------------
    # Main Process
    # --------------------------------------------------

    async def process(
        self,
        input_file: Path,
        output_dir: Path,
        settings: ProcessorSettings,
        progress_callback=None,
        pause_callback=None,
    ) -> Path:

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        duration = await self.duration(
            input_file
        )

        output, command = await self.build_command(
            input_file,
            output_dir,
            settings,
        )

        await self.execute_with_progress(
            command,
            duration,
            progress_callback,
            pause_callback,
        )

        if not output.exists():

            raise FileNotFoundError(
                "FFmpeg output missing."
            )

        return output

    # --------------------------------------------------
    # Check Hardware
    # --------------------------------------------------

    async def hardware_acceleration(
        self,
    ) -> str | None:

        process = await asyncio.create_subprocess_exec(
            self.ffmpeg,
            "-encoders",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )

        stdout, _ = await process.communicate()

        encoders = stdout.decode(
            errors="ignore"
        )

        if "h264_nvenc" in encoders:

            return "nvenc"

        if "h264_qsv" in encoders:

            return "qsv"

        if "h264_vaapi" in encoders:

            return "vaapi"

        return None
