"""Dots pattern implementation"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Pattern

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vood.core.color import Color


@dataclass(frozen=True)
class DotsPattern(Pattern):
    """Dot pattern with dots arranged in a grid

    Args:
        spacing: Distance between dot centers
        dot_radius: Radius of each dot
        dot_color: Color of the dots
        background: Optional background color

    Example:
        >>> pattern = DotsPattern(
        ...     spacing=20,
        ...     dot_radius=3,
        ...     dot_color=Color("#3498db"),
        ...     background=Color("#ecf0f1")
        ... )
    """

    spacing: float
    dot_radius: float
    dot_color: Color
    background: Optional[Color] = None

    def __post_init__(self):
        if self.spacing <= 0:
            raise ValueError(f"spacing must be > 0, got {self.spacing}")
        if self.dot_radius <= 0:
            raise ValueError(f"dot_radius must be > 0, got {self.dot_radius}")

    def to_drawsvg(self, drawing: Optional[dw.Drawing] = None) -> dw.Pattern:
        """Convert to drawsvg Pattern object"""
        from vood.component import CircleState, CircleRenderer, RectangleState, RectangleRenderer

        import uuid

        pattern_id = f"pattern-{uuid.uuid4().hex[:8]}"

        pattern = dw.Pattern(
            width=self.spacing,
            height=self.spacing,
            x=0,
            y=0,
            patternUnits="userSpaceOnUse",
            id=pattern_id
        )

        # Add background if specified
        if self.background and not self.background.is_none():
            bg_state = RectangleState(
                x=self.spacing/2, y=self.spacing/2,
                width=self.spacing, height=self.spacing,
                fill_color=self.background
            )
            bg_element = RectangleRenderer().render(bg_state, drawing)
            pattern.append(bg_element)

        # Add dot in center
        dot_state = CircleState(
            x=self.spacing/2, y=self.spacing/2,
            radius=self.dot_radius,
            fill_color=self.dot_color
        )
        dot_element = CircleRenderer().render(dot_state, drawing)
        pattern.append(dot_element)

        return pattern

    def interpolate(self, other: Pattern, t: float):
        """Interpolate between two DotsPattern instances"""
        if not isinstance(other, DotsPattern):
            # Step interpolation for different pattern types
            return self if t < 0.5 else other

        # Interpolate numeric values
        spacing = self.spacing + (other.spacing - self.spacing) * t
        dot_radius = self.dot_radius + (other.dot_radius - self.dot_radius) * t

        # Interpolate colors
        dot_color = self.dot_color.interpolate(other.dot_color, t)

        # Handle background interpolation
        if self.background and other.background:
            background = self.background.interpolate(other.background, t)
        elif t < 0.5:
            background = self.background
        else:
            background = other.background

        return DotsPattern(
            spacing=spacing,
            dot_radius=dot_radius,
            dot_color=dot_color,
            background=background
        )


