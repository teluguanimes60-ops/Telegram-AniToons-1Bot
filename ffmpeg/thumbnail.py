"""
ffmpeg/thumbnail.py

Thumbnail generation utilities.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from PIL import Image

from logger import get_logger

log = get_logger(__name__)


async def generate_thumbnail(
    media_path: Path,
    output: Path | None = None,
    timestamp: str = "00:00:01",
) -> Path | None:
    """
    Generate thumbnail from a video using FFmpeg.
    """

    if output is None:
        output = media_path.with_suffix(".jpg")

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        timestamp,
        "-i",
        str(media_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output),
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )

    await process.wait()

    if process.returncode != 0:
        log.error(
            "Thumbnail generation failed: %s",
            media_path,
        )
        return None

    return output


async def resize_thumbnail(
    image_path: Path,
    width: int,
    height: int,
) -> Path:
    """
    Resize thumbnail while keeping aspect ratio.
    """

    img = Image.open(image_path)

    img.thumbnail((width, height))

    img.save(
        image_path,
        quality=95,
    )

    return image_path


async def crop_thumbnail(
    image_path: Path,
    width: int,
    height: int,
) -> Path:
    """
    Center crop thumbnail.
    """

    img = Image.open(image_path)

    img = img.crop(
        (
            max(0, (img.width - width) // 2),
            max(0, (img.height - height) // 2),
            max(width, (img.width + width) // 2),
            max(height, (img.height + height) // 2),
        )
    )

    img.save(image_path)

    return image_path


async def remove_thumbnail(
    image_path: Path,
) -> None:

    try:

        if image_path.exists():
            image_path.unlink()

    except Exception:

        log.exception(
            "Failed removing thumbnail."
        )

  """
ffmpeg/thumbnail.py

Part 2
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


# --------------------------------------------------
# JPEG Optimization
# --------------------------------------------------

async def optimize_thumbnail(
    image_path: Path,
    quality: int = 90,
) -> Path:

    with Image.open(image_path) as image:

        image = image.convert("RGB")

        image.save(
            image_path,
            format="JPEG",
            optimize=True,
            quality=quality,
        )

    return image_path


# --------------------------------------------------
# Blur
# --------------------------------------------------

async def blur_thumbnail(
    image_path: Path,
    radius: int = 2,
) -> Path:

    with Image.open(image_path) as image:

        image = image.filter(
            ImageFilter.GaussianBlur(radius)
        )

        image.save(image_path)

    return image_path


# --------------------------------------------------
# Watermark
# --------------------------------------------------

async def watermark_thumbnail(
    image_path: Path,
    text: str,
) -> Path:

    with Image.open(image_path) as image:

        image = image.convert("RGB")

        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(
                "arial.ttf",
                20,
            )
        except Exception:
            font = ImageFont.load_default()

        x = 10
        y = image.height - 35

        draw.rectangle(
            (
                x - 5,
                y - 5,
                x + 220,
                y + 28,
            ),
            fill=(0, 0, 0),
        )

        draw.text(
            (x, y),
            text,
            fill="white",
            font=font,
        )

        image.save(image_path)

    return image_path


# --------------------------------------------------
# Square Thumbnail
# --------------------------------------------------

async def square_thumbnail(
    image_path: Path,
    size: int = 320,
) -> Path:

    with Image.open(image_path) as image:

        image = image.convert("RGB")

        image.thumbnail((size, size))

        canvas = Image.new(
            "RGB",
            (size, size),
            "black",
        )

        x = (size - image.width) // 2
        y = (size - image.height) // 2

        canvas.paste(image, (x, y))

        canvas.save(
            image_path,
            quality=90,
        )

    return image_path


# --------------------------------------------------
# Telegram Validation
# --------------------------------------------------

async def validate_thumbnail(
    image_path: Path,
) -> bool:

    if not image_path.exists():
        return False

    if image_path.stat().st_size == 0:
        return False

    try:

        with Image.open(image_path) as image:
            image.verify()

    except Exception:
        return False

    return True
