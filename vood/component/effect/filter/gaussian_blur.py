"""Gaussian blur filter"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Filter


@dataclass(frozen=True)
class GaussianBlurFilter(Filter):
    """Gaussian blur filter effect

    Args:
        std_deviation: Standard deviation of the blur (higher = more blur)
        std_deviation_x: Optional separate x-axis blur (overrides std_deviation)
        std_deviation_y: Optional separate y-axis blur (overrides std_deviation)

    Example:
        >>> blur = BlurFilter(std_deviation=5.0)
        >>> # Separate x/y blur:
        >>> blur_directional = BlurFilter(std_deviation_x=10.0, std_deviation_y=2.0)
    """

    std_deviation: float = 0.0
    std_deviation_x: Optional[float] = None
    std_deviation_y: Optional[float] = None

    def __post_init__(self):
        if self.std_deviation < 0:
            raise ValueError(f"std_deviation must be >= 0, got {self.std_deviation}")
        if self.std_deviation_x is not None and self.std_deviation_x < 0:
            raise ValueError(
                f"std_deviation_x must be >= 0, got {self.std_deviation_x}"
            )
        if self.std_deviation_y is not None and self.std_deviation_y < 0:
            raise ValueError(
                f"std_deviation_y must be >= 0, got {self.std_deviation_y}"
            )

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        if self.std_deviation_x is not None or self.std_deviation_y is not None:
            std_x = (
                self.std_deviation_x
                if self.std_deviation_x is not None
                else self.std_deviation
            )
            std_y = (
                self.std_deviation_y
                if self.std_deviation_y is not None
                else self.std_deviation
            )
            std_dev_str = f"{std_x} {std_y}"
        else:
            std_dev_str = str(self.std_deviation)

        return dw.FilterItem(
            "feGaussianBlur", stdDeviation=std_dev_str, in_="SourceGraphic"
        )

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two BlurFilter instances"""
        if not isinstance(other, GaussianBlurFilter):
            return self if t < 0.5 else other

        # Interpolate standard deviation
        std_deviation = (
            self.std_deviation + (other.std_deviation - self.std_deviation) * t
        )

        # Handle optional x/y deviations
        if self.std_deviation_x is not None and other.std_deviation_x is not None:
            std_deviation_x = (
                self.std_deviation_x
                + (other.std_deviation_x - self.std_deviation_x) * t
            )
        elif t < 0.5:
            std_deviation_x = self.std_deviation_x
        else:
            std_deviation_x = other.std_deviation_x

        if self.std_deviation_y is not None and other.std_deviation_y is not None:
            std_deviation_y = (
                self.std_deviation_y
                + (other.std_deviation_y - self.std_deviation_y) * t
            )
        elif t < 0.5:
            std_deviation_y = self.std_deviation_y
        else:
            std_deviation_y = other.std_deviation_y

        return GaussianBlurFilter(
            std_deviation=std_deviation,
            std_deviation_x=std_deviation_x,
            std_deviation_y=std_deviation_y,
        )
