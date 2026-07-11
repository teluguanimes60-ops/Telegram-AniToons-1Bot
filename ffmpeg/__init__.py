"""
AniToons Bot
FFmpeg Package

Central exports for all FFmpeg helpers.
"""

from .processor import FFmpegProcessor
from .thumbnail import (
    generate_thumbnail,
    resize_thumbnail,
    crop_thumbnail,
    blur_thumbnail,
    watermark_thumbnail,
    optimize_thumbnail,
    square_thumbnail,
    validate_thumbnail,
)

__all__ = [
    "FFmpegProcessor",
    "generate_thumbnail",
    "resize_thumbnail",
    "crop_thumbnail",
    "blur_thumbnail",
    "watermark_thumbnail",
    "optimize_thumbnail",
    "square_thumbnail",
    "validate_thumbnail",
]
