"""Rectangle renderer implementation using new architecture"""

from __future__ import annotations

import drawsvg as dw

from .base import Renderer

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
        fill_color = state.color.to_rgb_string()

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
            rect_kwargs["stroke"] = state.stroke_color.to_rgb_string()
            rect_kwargs["stroke_width"] = state.stroke_width

        return dw.Rectangle(**rect_kwargs)
