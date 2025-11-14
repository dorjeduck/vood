"""Circle renderer implementation using new architecture"""

from __future__ import annotations

import drawsvg as dw

from .base import Renderer

from vood.components.states import CircleState


class CircleRenderer(Renderer):
    """Renderer class for rendering circle elements

    The radius is now part of the state, making it animatable!
    """

    def __init__(self) -> None:
        """Initialize circle renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(self, state: CircleState) -> dw.Circle:
        """Render the core circle geometry centered at origin (0,0)"""
        circle_kwargs = {
            "cx": 0,
            "cy": 0,
            "r": state.radius,
        }
        if state.color:
            fill_color = state.color.to_rgb_string()
            circle_kwargs["fill"] = fill_color
        else:
            circle_kwargs["fill"] = "none"  # No fill if color is None

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            circle_kwargs["stroke"] = state.stroke_color.to_rgb_string()
            circle_kwargs["stroke_width"] = state.stroke_width

        return dw.Circle(**circle_kwargs)
