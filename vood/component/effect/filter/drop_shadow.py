"""Drop shadow filter"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Filter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vood.core.color import Color


@dataclass(frozen=True)
class DropShadowFilter(Filter):
    """Drop shadow filter effect

    Args:
        dx: Horizontal offset of the shadow
        dy: Vertical offset of the shadow
        std_deviation: Blur amount for the shadow
        color: Shadow color (default: semi-transparent black)
        opacity: Shadow opacity (0-1)

    Example:
        >>> from vood.core import Color
        >>> shadow = DropShadowFilter(dx=5, dy=5, std_deviation=3, color=Color("#000000"), opacity=0.5)
    """

    dx: float = 2.0
    dy: float = 2.0
    std_deviation: float = 2.0
    color: Optional[Color] = None
    opacity: float = 1.0

    def __post_init__(self):
        if self.std_deviation < 0:
            raise ValueError(f"std_deviation must be >= 0, got {self.std_deviation}")
        if not 0 <= self.opacity <= 1:
            raise ValueError(f"opacity must be between 0 and 1, got {self.opacity}")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        # Default to semi-transparent black if no color specified
        from vood.core.color import Color
        color = self.color if self.color else Color("#000000")

        return dw.FilterItem(
            'feDropShadow',
            dx=self.dx,
            dy=self.dy,
            stdDeviation=self.std_deviation,
            flood_color=color.to_rgb_string(),
            flood_opacity=self.opacity
        )

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two DropShadowFilter instances"""
        if not isinstance(other, DropShadowFilter):
            return self if t < 0.5 else other

        from vood.core.color import Color

        # Interpolate numeric values
        dx = self.dx + (other.dx - self.dx) * t
        dy = self.dy + (other.dy - self.dy) * t
        std_deviation = self.std_deviation + (other.std_deviation - self.std_deviation) * t
        opacity = self.opacity + (other.opacity - self.opacity) * t

        # Interpolate color if both filters have colors
        default_color = Color("#000000")
        self_color = self.color if self.color else default_color
        other_color = other.color if other.color else default_color
        color = self_color.interpolate(other_color, t)

        return DropShadowFilter(
            dx=dx,
            dy=dy,
            std_deviation=std_deviation,
            color=color,
            opacity=opacity
        )


