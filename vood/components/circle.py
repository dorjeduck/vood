"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

import drawsvg as dw

from vood.components import Renderer, State
from vood.transitions import Easing

from vood.utils import to_rgb_string


@dataclass
class CircleState(State):
    """State class for circle elements

    """

    radius: float = 50
    color: Optional[Tuple[int, int, int]] = (255, 0, 0)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0

    # Default easing functions for each property
    DEFAULT_EASING = {
        "x": Easing.in_out,
        "y": Easing.in_out,
        "scale": Easing.in_out,
        "opacity": Easing.linear,
        "radius": Easing.in_out,
        "color": Easing.linear,
        "stroke_color": Easing.linear,
        "stroke_width": Easing.in_out,
    }


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
