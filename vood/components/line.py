"""Line renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

import math
import drawsvg as dw

from vood.components import Renderer, State
from vood.utils import to_rgb_string
from vood.transitions import Easing


@dataclass
class LineState(State):
    """State class for line elements"""

    length: float = 100  # Length of the line
    color: Tuple[int, int, int] = (220, 220, 220)
    stroke_width: float = 1
    stroke_dasharray: Optional[str] = None  # For dashed lines, e.g., "5,5"
    stroke_linecap: str = "round"  # "butt", "round", "square"

    DEFAULT_EASING = {
        "x": Easing.in_out,
        "y": Easing.in_out,
        "length": Easing.in_out,
        "scale": Easing.in_out,
        "rotation": Easing.in_out,
        "opacity": Easing.linear,
        "color": Easing.linear,
        "stroke_width": Easing.in_out,
        "stroke_dasharray": Easing.linear,  # Stepped animation for strings
        "stroke_linecap": Easing.linear,  # Stepped animation for strings
    }


class LineRenderer(Renderer):
    @staticmethod
    def from_endpoints(x1: float, y1: float, x2: float, y2: float):
        """
        Given two endpoints, return center (x, y), length, and rotation (degrees).
        Returns:
            (center_x, center_y, length, rotation)
        """

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        rotation = math.degrees(math.atan2(dy, dx))
        return center_x, center_y, length, rotation

    """Renderer class for rendering line elements"""

    def _render_core(self, state: LineState) -> dw.Line:
        """Render the line renderer (geometry only, no transforms)

        Args:
            state: The state object containing properties for rendering

        Returns:
            drawsvg Line object representing the line renderer
        """

        stroke_color = to_rgb_string(state.color)

        # Create line with basic properties
        line_kwargs = {
            "stroke": stroke_color,
            "stroke_width": state.stroke_width,
            "stroke_linecap": state.stroke_linecap,
            "fill": "none",  # Lines don't have fill
        }

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
