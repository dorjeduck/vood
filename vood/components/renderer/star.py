"""Star renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import math
import drawsvg as dw

from .base import Renderer
from vood.utils import to_rgb_string


from vood.components.states import StarState


class StarRenderer(Renderer):
    """Renderer class for rendering star elements"""

    def _render_core(self, state: StarState) -> dw.Lines:
        """Render the star renderer (geometry only) with the given state

        Args:
            state (StarState): The state of the star renderer.

        Returns:
            drawsvg Lines object for the star renderer geometry.
        """

        fill_color = to_rgb_string(state.color)

        # Calculate star points
        coords = []
        num_points = max(3, state.points)  # Minimum 3 points

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
        lines_kwargs = {"fill": fill_color, "close": True}  # Close the polygon

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            lines_kwargs["stroke"] = to_rgb_string(state.stroke_color)
            lines_kwargs["stroke_width"] = state.stroke_width

        # Create Lines with flattened coordinates
        return dw.Lines(*coords, **lines_kwargs)
