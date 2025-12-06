"""Custom pattern implementation"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Pattern

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vood.core.color import Color
    
from typing import Any


@dataclass(frozen=True)
class CustomPattern(Pattern):
    """Custom pattern with arbitrary content

    A pattern defines a small graphic tile that repeats to fill a shape.
    The pattern tile can contain any shapes (circles, rectangles, paths, etc.)

    Args:
        width: Pattern tile width
        height: Pattern tile height
        content: Tuple of (state, renderer) pairs defining pattern content
        pattern_units: "userSpaceOnUse" or "objectBoundingBox"

    Example:
        >>> from vood.component import CircleState, CircleRenderer
        >>> from vood.core import Color
        >>> # Custom pattern with circle
        >>> circle_state = CircleState(x=10, y=10, radius=5, fill_color=Color("red"))
        >>> circle_renderer = CircleRenderer()
        >>> pattern = CustomPattern(
        ...     width=20,
        ...     height=20,
        ...     content=((circle_state, circle_renderer),)
        ... )
    """

    width: float
    height: float
    content: tuple[tuple[Any, Any], ...]  # (state, renderer) pairs
    pattern_units: str = "userSpaceOnUse"

    def __post_init__(self):
        if self.width <= 0:
            raise ValueError(f"width must be > 0, got {self.width}")
        if self.height <= 0:
            raise ValueError(f"height must be > 0, got {self.height}")
        if not self.content:
            raise ValueError("Pattern must have at least one content item")

    def to_drawsvg(self, drawing: Optional[dw.Drawing] = None) -> dw.Pattern:
        """Convert to drawsvg Pattern object"""
        pattern = dw.Pattern(
            width=self.width,
            height=self.height,
            x=0,
            y=0,
            patternUnits=self.pattern_units
        )

        # Render each content item into the pattern
        for state, renderer in self.content:
            element = renderer.render(state, drawing)
            pattern.append(element)

        return pattern

    def interpolate(self, other: Pattern, t: float):
        """Custom patterns use step interpolation"""
        return self if t < 0.5 else other


