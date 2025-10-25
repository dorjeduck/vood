"""Triangle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import math

import drawsvg as dw

from vood.components import Renderer, State
from vood.utils import to_rgb_string
from vood.transitions import Easing


@dataclass
class TriangleState(State):
    """State class for triangle elements"""

    size: float = 50  # Size of the triangle (distance from center to vertex)
    color: Tuple[int, int, int] = (255, 255, 0)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0

    DEFAULT_EASING = {
        "x": Easing.in_out,
        "y": Easing.in_out,
        "scale": Easing.in_out,
        "rotation": Easing.in_out,
        "opacity": Easing.linear,
        "size": Easing.in_out,
        "color": Easing.linear,
        "stroke_color": Easing.linear,
        "stroke_width": Easing.in_out,
    }


class TriangleRenderer(Renderer):
    """Renderer class for rendering triangle elements

    Creates an equilateral triangle pointing upward
    """

    def _render_core(self, state: TriangleState) -> dw.Lines:
        """Render the triangle renderer (geometry only)

        Args:
            state: The TriangleState containing properties for rendering

        Returns:
            drawsvg Lines object for the triangle renderer
        """
        fill_color = to_rgb_string(state.color)

        # Calculate equilateral triangle points with scaling
       
        height_offset = state.size
        width_offset = state.size * math.sqrt(3) / 2

        # Base triangle points (centered at origin)
        points = [
            (0, -height_offset),  # Top vertex
            (-width_offset, height_offset / 2),  # Bottom left
            (width_offset, height_offset / 2),  # Bottom right
        ]

        # Remove manual rotation, let base class handle it

        # Flatten coordinates
        coords = []
        for px, py in points:
            coords.extend([px, py])

        # Create lines with triangle points (flattened coordinates)
        lines_kwargs = {"fill": fill_color, "close": True}  # Close the polygon

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            lines_kwargs["stroke"] = to_rgb_string(state.stroke_color)
            lines_kwargs["stroke_width"] = state.stroke_width

        # Create Lines with flattened coordinates
        return dw.Lines(*coords, **lines_kwargs)
