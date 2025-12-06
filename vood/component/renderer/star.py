"""Star renderer implementation using new architecture"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import math
import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.star import StarState




class StarRenderer(Renderer):
    """Renderer class for rendering star elements"""

    def _render_core(
        self, state: "StarState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Lines:
        """Render the star renderer (geometry only) with the given state

        Args:
            state (StarState): The state of the star renderer.

        Returns:
            drawsvg Lines object for the star renderer geometry.
        """

        fill_color = state.fill_color.to_rgb_string()

        # Calculate star points
        coords = []
        num_points = max(3, state.num_points_star)  # Minimum 3 points

        for i in range(num_points * 2):  # Double for inner and outer points
            angle = (i * math.pi) / num_points - math.pi / 2  # Start from top
            if i % 2 == 0:  # Outer points
                radius = state.outer_radius
            else:  # Inner points
                radius = state.inner_radius

            # Remove manual rotation
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            coords.extend([x, y])  # Flatten coordinates for Lines

        # Create lines with star points
        lines_kwargs = {
            "close": True,
        }  # Close the polygon
        self._set_fill_and_stroke_kwargs(state, lines_kwargs, drawing)

        # Create Lines with flattened coordinates
        return dw.Lines(*coords, **lines_kwargs)
