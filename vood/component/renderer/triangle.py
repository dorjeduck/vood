"""Triangle renderer implementation using new architecture"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import math

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.triangle import TriangleState



class TriangleRenderer(Renderer):
    """Renderer class for rendering triangle elements

    Creates an equilateral triangle pointing upward
    """

    def _render_core(
        self, state: "TriangleState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Lines:
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
            "close": True,
        }  # Close the polygon
        self._set_fill_and_stroke_kwargs(state, lines_kwargs, drawing)


        # Create Lines with flattened coordinates
        return dw.Lines(*coords, **lines_kwargs)
