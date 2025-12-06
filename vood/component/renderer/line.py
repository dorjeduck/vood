"""Line renderer implementation using new architecture"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional


import math
import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.line import LineState


class LineRenderer(Renderer):
    @staticmethod
    def from_endpoints(x1: float, y1: float, x2: float, y2: float):
        """
        Given two endpoints, return center (x, y), length, and rotation (degrees).
        Returns:
            (cx, cy, length, rotation)
        """

        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        rotation = math.degrees(math.atan2(dy, dx))
        return cx, cy, length, rotation

    """Renderer class for rendering line elements"""

    def _render_core(
        self, state: "LineState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Line:
        """Render the line renderer (geometry only, no transforms)

        Args:
            state: The state object containing properties for rendering

        Returns:
            drawsvg Line object representing the line renderer
        """

        # Create line with basic properties
        line_kwargs = {
            "stroke_linecap": state.stroke_linecap,
        }
        self._set_fill_and_stroke_kwargs(state, line_kwargs, drawing)
        # Add stroke dash array if specified
        if state.stroke_dasharray:
            line_kwargs["stroke_dasharray"] = state.stroke_dasharray

        # Remove manual opacity and rotation
        half_length = state.length / 2

        # Center at origin, let base handle translation and rotation
        start_x = -half_length
        start_y = 0

        end_x = half_length
        end_y = 0

        # Line constructor takes (sx, sy, ex, ey, **kwargs)
        return dw.Line(start_x, start_y, end_x, end_y, **line_kwargs)
