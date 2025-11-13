"""Rectangle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

import drawsvg as dw

from .base import Renderer
from vood.utils import to_rgb_string
from vood.transitions import easing
from vood.utils.colors import hex_to_color

from vood.components.states import RectangleState


class RectangleRenderer(Renderer):
    """Renderer class for rendering rectangle elements"""

    def _render_core(self, state: RectangleState) -> dw.Rectangle:
        """Render the rectangle renderer (geometry only, no transforms)

        Args:
            state (RectangleState): The state of the rectangle

        Returns:
            dw.Rectangle: The drawsvg rectangle object
        """
        fill_color = to_rgb_string(state.color)

        # Create rectangle centered at origin with scaled dimensions
        rect_kwargs = {
            "x": -(state.width) / 2,  # Center the rectangle
            "y": -(state.height) / 2,
            "width": state.width,
            "height": state.height,
            "fill": fill_color,
        }

        # Add corner radius if specified
        if state.corner_radius > 0:
            rect_kwargs["rx"] = state.corner_radius
            rect_kwargs["ry"] = state.corner_radius

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            rect_kwargs["stroke"] = to_rgb_string(state.stroke_color)
            rect_kwargs["stroke_width"] = state.stroke_width

        return dw.Rectangle(**rect_kwargs)
