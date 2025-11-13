"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from typing import Optional

import drawsvg as dw

from .base import Renderer

from ..state.circle import CircleState


class CircleRenderer(Renderer):
    """Renderer class for rendering circle elements

    The radius is now part of the state, making it animatable!
    """

    def __init__(self) -> None:
        """Initialize circle renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(self, state: CircleState, drawing: Optional[dw.Drawing] = None) -> dw.Circle:
        """Render the core circle geometry centered at origin (0,0)"""
        circle_kwargs = {
            "cx": 0,
            "cy": 0,
            "r": state.radius,
        }
        if state.fill_color:
            fill_color = state.fill_color.to_rgb_string()
            circle_kwargs["fill"] = fill_color
            circle_kwargs["fill_opacity"] = state.fill_opacity
        else:
            circle_kwargs["fill"] = "none"  # No fill if color is None

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:

            circle_kwargs["stroke"] = state.stroke_color.to_rgb_string()
            circle_kwargs["stroke_width"] = state.stroke_width
            circle_kwargs["stroke_opacity"] = state.stroke_opacity

        return dw.Circle(**circle_kwargs)
