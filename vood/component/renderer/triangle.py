"""Triangle renderer implementation using new architecture"""

from __future__ import annotations
from typing import Optional

import math

import drawsvg as dw

from .base import Renderer
from ..state.triangle import TriangleState


class TriangleRenderer(Renderer):
    """Renderer class for rendering triangle elements

    Creates an equilateral triangle pointing upward
    """

    def _render_core(self, state: TriangleState, drawing: Optional[dw.Drawing] = None) -> dw.Lines:
        """Render the triangle renderer (geometry only)

        Args:
            state: The TriangleState containing properties for rendering

        Returns:
            drawsvg Lines object for the triangle renderer
        """
        fill_color = state.fill_color.to_rgb_string()

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
        coords = [coord for px, py in points for coord in (px, py)]

        # Create lines with triangle points (flattened coordinates)
        lines_kwargs = {
            "fill": fill_color,
            "fill_opacity": state.fill_opacity,
            "close": True,
        }  # Close the polygon

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            lines_kwargs["stroke"] = state.stroke_color.to_rgb_string()
            lines_kwargs["stroke_opacity"] = state.stroke_opacity
            lines_kwargs["stroke_width"] = state.stroke_width

        # Create Lines with flattened coordinates
        return dw.Lines(*coords, **lines_kwargs)
