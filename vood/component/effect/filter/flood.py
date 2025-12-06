"""Flood filter"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Filter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vood.core.color import Color


@dataclass(frozen=True)
class FloodFilter(Filter):
    """Flood filter - fills filter region with solid color

    Args:
        flood_color: Color to flood
        flood_opacity: Opacity of flood (0-1)

    Example:
        >>> from vood.core import Color
        >>> flood = FloodFilter(flood_color=Color("#ff0000"), flood_opacity=0.5)
    """

    flood_color: Color
    flood_opacity: float = 1.0

    def __post_init__(self):
        if not 0 <= self.flood_opacity <= 1:
            raise ValueError(f"flood_opacity must be between 0 and 1, got {self.flood_opacity}")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        return dw.FilterItem(
            'feFlood',
            flood_color=self.flood_color.to_rgb_string(),
            flood_opacity=self.flood_opacity
        )

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two FloodFilter instances"""
        if not isinstance(other, FloodFilter):
            return self if t < 0.5 else other

        flood_color = self.flood_color.interpolate(other.flood_color, t)
        flood_opacity = self.flood_opacity + (other.flood_opacity - self.flood_opacity) * t

        return FloodFilter(flood_color=flood_color, flood_opacity=flood_opacity)


