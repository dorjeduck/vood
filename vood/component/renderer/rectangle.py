"""Rectangle renderer implementation using new architecture"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.rectangle import RectangleState




class RectangleRenderer(Renderer):
    """Renderer class for rendering rectangle elements"""

    def _render_core(
        self, state: "RectangleState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Rectangle:
        """Render the rectangle renderer (geometry only, no transforms)

        Args:
            state (RectangleState): The state of the rectangle

        Returns:
            dw.Rectangle: The drawsvg rectangle object
        """
        fill_color = state.fill_color.to_rgb_string()

        # Create rectangle centered at origin with scaled dimensions
        rect_kwargs = {
            "x": -(state.width) / 2,  # Center the rectangle
            "y": -(state.height) / 2,
            "width": state.width,
            "height": state.height,
            "fill": fill_color,
        }

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            rect_kwargs["stroke"] = state.stroke_color.to_rgb_string()
            rect_kwargs["stroke_opacity"] = state.stroke_opacity
            rect_kwargs["stroke_width"] = state.stroke_width

        return dw.Rectangle(**rect_kwargs)
