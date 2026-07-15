"""
helpers/watermark.py

Watermark helper for AniToons Bot.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class WatermarkHelper:
    """Image watermark helper."""

    DEFAULT_FONT_SIZE = 28

    DEFAULT_MARGIN = 15

    # --------------------------------------------------
    # Load Font
    # --------------------------------------------------

    def load_font(
        self,
        size: int,
    ):

        try:
            return ImageFont.truetype(
                "arial.ttf",
                size,
            )

        except Exception:
            return ImageFont.load_default()

    # --------------------------------------------------
    # Text Watermark
    # --------------------------------------------------

    async def add_text(
        self,
        image: str | Path,
        text: str,
        output: str | Path | None = None,
        *,
        font_size: int = DEFAULT_FONT_SIZE,
    ) -> Path:

        image = Path(image)

        if output is None:
            output = image

        output = Path(output)

        with Image.open(image).convert("RGBA") as base:

            overlay = Image.new(
                "RGBA",
                base.size,
                (255, 255, 255, 0),
            )

            draw = ImageDraw.Draw(overlay)

            font = self.load_font(font_size)

            bbox = draw.textbbox(
                (0, 0),
                text,
                font=font,
            )

            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]

            x = (
                base.width
                - width
                - self.DEFAULT_MARGIN
            )

            y = (
                base.height
                - height
                - self.DEFAULT_MARGIN
            )

            draw.rectangle(
                (
                    x - 6,
                    y - 6,
                    x + width + 6,
                    y + height + 6,
                ),
                fill=(0, 0, 0, 120),
            )

            draw.text(
                (x, y),
                text,
                font=font,
                fill=(255, 255, 255, 255),
            )

            merged = Image.alpha_composite(
                base,
                overlay,
            )

            merged.convert("RGB").save(
                output,
                quality=95,
            )

        return output

    # --------------------------------------------------
    # Image Watermark
    # --------------------------------------------------

    async def add_logo(
        self,
        image: str | Path,
        logo: str | Path,
        output: str | Path | None = None,
        *,
        scale: float = 0.20,
    ) -> Path:

        image = Path(image)

        logo = Path(logo)

        if output is None:
            output = image

        output = Path(output)

        with Image.open(image).convert("RGBA") as base:

            with Image.open(logo).convert("RGBA") as mark:

                width = int(base.width * scale)

                ratio = width / mark.width

                height = int(mark.height * ratio)

                mark = mark.resize(
                    (width, height)
                )

                x = (
                    base.width
                    - width
                    - self.DEFAULT_MARGIN
                )

                y = (
                    base.height
                    - height
                    - self.DEFAULT_MARGIN
                )

                base.alpha_composite(
                    mark,
                    (x, y),
                )

                base.convert("RGB").save(
                    output,
                    quality=95,
                )

        return output

    # --------------------------------------------------
    # Remove Transparency
    # --------------------------------------------------

    async def flatten(
        self,
        image: str | Path,
    ) -> Path:

        image = Path(image)

        with Image.open(image) as img:

            img.convert("RGB").save(
                image,
                quality=95,
            )

        return image


watermark_helper = WatermarkHelper()
