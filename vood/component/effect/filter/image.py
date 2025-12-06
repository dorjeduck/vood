"""Image filter"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Filter


@dataclass(frozen=True)
class ImageFilter(Filter):
    """Image filter - references an external image

    Args:
        href: URL or data URI of the image
        preserve_aspect_ratio: How to preserve aspect ratio

    Example:
        >>> img = ImageFilter(href='image.png')
    """

    href: str
    preserve_aspect_ratio: str = 'xMidYMid meet'

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        # Note: feImage uses xlink:href or href depending on SVG version
        return dw.FilterItem(
            'feImage',
            href=self.href,
            preserveAspectRatio=self.preserve_aspect_ratio
        )

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two ImageFilter instances"""
        if not isinstance(other, ImageFilter):
            return self if t < 0.5 else other

        # Step interpolation
        return self if t < 0.5 else other


