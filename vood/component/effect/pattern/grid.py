"""Grid pattern implementation"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Pattern

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vood.core.color import Color


@dataclass(frozen=True)
class GridPattern(Pattern):
    """Grid pattern with horizontal and vertical lines

    Args:
        spacing: Distance between grid lines
        line_width: Width of grid lines
        line_color: Color of grid lines
        background: Optional background color

    Example:
        >>> pattern = GridPattern(
        ...     spacing=30,
        ...     line_width=2,
        ...     line_color=Color("#34495e"),
        ...     background=Color("#ecf0f1")
        ... )
    """

    spacing: float
    line_width: float
    line_color: Color
    background: Optional[Color] = None

    def __post_init__(self):
        if self.spacing <= 0:
            raise ValueError(f"spacing must be > 0, got {self.spacing}")
        if self.line_width <= 0:
            raise ValueError(f"line_width must be > 0, got {self.line_width}")

    def to_drawsvg(self, drawing: Optional[dw.Drawing] = None) -> dw.Pattern:
        """Convert to drawsvg Pattern object"""
        from vood.component import RectangleState, RectangleRenderer

        pattern = dw.Pattern(
            width=self.spacing,
            height=self.spacing,
            x=0,
            y=0,
            patternUnits="userSpaceOnUse"
        )

        renderer = RectangleRenderer()

        # Add background if specified
        if self.background and not self.background.is_none():
            bg_state = RectangleState(
                x=self.spacing/2, y=self.spacing/2,
                width=self.spacing, height=self.spacing,
                fill_color=self.background
            )
            pattern.append(renderer.render(bg_state, drawing))

        # Add vertical line
        vline_state = RectangleState(
            x=self.line_width/2, y=self.spacing/2,
            width=self.line_width, height=self.spacing,
            fill_color=self.line_color
        )
        pattern.append(renderer.render(vline_state, drawing))

        # Add horizontal line
        hline_state = RectangleState(
            x=self.spacing/2, y=self.line_width/2,
            width=self.spacing, height=self.line_width,
            fill_color=self.line_color
        )
        pattern.append(renderer.render(hline_state, drawing))

        return pattern

    def interpolate(self, other: Pattern, t: float):
        """Interpolate between two GridPattern instances"""
        if not isinstance(other, GridPattern):
            # Step interpolation for different pattern types
            return self if t < 0.5 else other

        # Interpolate numeric values
        spacing = self.spacing + (other.spacing - self.spacing) * t
        line_width = self.line_width + (other.line_width - self.line_width) * t

        # Interpolate colors
        line_color = self.line_color.interpolate(other.line_color, t)

        # Handle background interpolation
        if self.background and other.background:
            background = self.background.interpolate(other.background, t)
        elif t < 0.5:
            background = self.background
        else:
            background = other.background

        return GridPattern(
            spacing=spacing,
            line_width=line_width,
            line_color=line_color,
            background=background
        )


