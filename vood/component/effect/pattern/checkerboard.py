"""Checkerboard pattern implementation"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Pattern

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vood.core.color import Color


@dataclass(frozen=True)
class CheckerboardPattern(Pattern):
    """Checkerboard pattern with alternating squares

    Args:
        square_size: Size of each square
        color1: Color of first square
        color2: Color of second square

    Example:
        >>> pattern = CheckerboardPattern(
        ...     square_size=20,
        ...     color1=Color("#2c3e50"),
        ...     color2=Color("#ecf0f1")
        ... )
    """

    square_size: float
    color1: Color
    color2: Color

    def __post_init__(self):
        if self.square_size <= 0:
            raise ValueError(f"square_size must be > 0, got {self.square_size}")

    def to_drawsvg(self, drawing: Optional[dw.Drawing] = None) -> dw.Pattern:
        """Convert to drawsvg Pattern object"""
        from vood.component import RectangleState, RectangleRenderer

        tile_size = self.square_size * 2

        pattern = dw.Pattern(
            width=tile_size,
            height=tile_size,
            x=0,
            y=0,
            patternUnits="userSpaceOnUse"
        )

        renderer = RectangleRenderer()

        # Top-left and bottom-right (color1)
        tl_state = RectangleState(
            x=self.square_size/2, y=self.square_size/2,
            width=self.square_size, height=self.square_size,
            fill_color=self.color1
        )
        pattern.append(renderer.render(tl_state, drawing))

        br_state = RectangleState(
            x=self.square_size * 1.5, y=self.square_size * 1.5,
            width=self.square_size, height=self.square_size,
            fill_color=self.color1
        )
        pattern.append(renderer.render(br_state, drawing))

        # Top-right and bottom-left (color2)
        tr_state = RectangleState(
            x=self.square_size * 1.5, y=self.square_size/2,
            width=self.square_size, height=self.square_size,
            fill_color=self.color2
        )
        pattern.append(renderer.render(tr_state, drawing))

        bl_state = RectangleState(
            x=self.square_size/2, y=self.square_size * 1.5,
            width=self.square_size, height=self.square_size,
            fill_color=self.color2
        )
        pattern.append(renderer.render(bl_state, drawing))

        return pattern

    def interpolate(self, other: Pattern, t: float):
        """Interpolate between two CheckerboardPattern instances"""
        if not isinstance(other, CheckerboardPattern):
            # Step interpolation for different pattern types
            return self if t < 0.5 else other

        # Interpolate numeric values
        square_size = self.square_size + (other.square_size - self.square_size) * t

        # Interpolate colors
        color1 = self.color1.interpolate(other.color1, t)
        color2 = self.color2.interpolate(other.color2, t)

        return CheckerboardPattern(
            square_size=square_size,
            color1=color1,
            color2=color2
        )
