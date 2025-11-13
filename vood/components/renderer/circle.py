"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

import drawsvg as dw

from .base import Renderer
from vood.transitions import easing

from vood.utils import to_rgb_string
from vood.utils.colors import hex_to_color

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
            fill_color = to_rgb_string(state.color)
            circle_kwargs["fill"] = fill_color
        else:
            circle_kwargs["fill"] = "none"  # No fill if color is None

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            circle_kwargs["stroke"] = to_rgb_string(state.stroke_color)
            circle_kwargs["stroke_width"] = state.stroke_width

        return dw.Circle(**circle_kwargs)
