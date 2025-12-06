"""Stripes pattern implementation"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Pattern

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vood.core.color import Color


@dataclass(frozen=True)
class StripesPattern(Pattern):
    """Stripe pattern with alternating colored stripes

    Args:
        stripe_width: Width of each stripe
        color1: Color of first stripe
        color2: Color of second stripe
        angle: Rotation angle in degrees (0 = horizontal, 90 = vertical)

    Example:
        >>> pattern = StripesPattern(
        ...     stripe_width=10,
        ...     color1=Color("#e74c3c"),
        ...     color2=Color("#c0392b"),
        ...     angle=45
        ... )
    """

    stripe_width: float
    color1: Color
    color2: Color
    angle: float = 0

    def __post_init__(self):
        if self.stripe_width <= 0:
            raise ValueError(f"stripe_width must be > 0, got {self.stripe_width}")

    def to_drawsvg(self, drawing: Optional[dw.Drawing] = None) -> dw.Pattern:
        """Convert to drawsvg Pattern object"""
        from vood.component import RectangleState, RectangleRenderer

        tile_size = self.stripe_width * 2

        pattern = dw.Pattern(
            width=tile_size,
            height=tile_size,
            x=0,
            y=0,
            patternUnits="userSpaceOnUse"
        )

        renderer = RectangleRenderer()

        # First stripe
        stripe1_state = RectangleState(
            x=0, y=tile_size/2,
            width=self.stripe_width, height=tile_size,
            fill_color=self.color1,
            rotation=self.angle
        )
        pattern.append(renderer.render(stripe1_state, drawing))

        # Second stripe
        stripe2_state = RectangleState(
            x=self.stripe_width, y=tile_size/2,
            width=self.stripe_width, height=tile_size,
            fill_color=self.color2,
            rotation=self.angle
        )
        pattern.append(renderer.render(stripe2_state, drawing))

        return pattern

    def interpolate(self, other: Pattern, t: float):
        """Interpolate between two StripesPattern instances"""
        if not isinstance(other, StripesPattern):
            # Step interpolation for different pattern types
            return self if t < 0.5 else other

        # Interpolate numeric values
        stripe_width = self.stripe_width + (other.stripe_width - self.stripe_width) * t
        angle = self.angle + (other.angle - self.angle) * t

        # Interpolate colors
        color1 = self.color1.interpolate(other.color1, t)
        color2 = self.color2.interpolate(other.color2, t)

        return StripesPattern(
            stripe_width=stripe_width,
            color1=color1,
            color2=color2,
            angle=angle
        )


