"""Ellipse renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

import drawsvg as dw

from vood.components import Renderer, State
from vood.utils import to_rgb_string
from vood.transitions import Easing


@dataclass
class EllipseState(State):
    """State class for ellipse elements"""

    rx: float = 60  # Horizontal radius
    ry: float = 40  # Vertical radius
    color: Tuple[int, int, int] = (0, 0, 255)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0

    DEFAULT_EASING = {
        "x": Easing.in_out,
        "y": Easing.in_out,
        "scale": Easing.in_out,
        "rotation": Easing.in_out,
        "opacity": Easing.linear,
        "rx": Easing.in_out,
        "ry": Easing.in_out,
        "color": Easing.linear,
        "stroke_color": Easing.linear,
        "stroke_width": Easing.in_out,
    }


class EllipseRenderer(Renderer):
    """Renderer class for rendering ellipse elements"""

    def __init__(self) -> None:
        """Initialize ellipse renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(self, state: EllipseState) -> dw.Ellipse:
        """Render the ellipse renderer (geometry only) with the given state

        Returns:
            drawsvg Ellipse object
        """
        fill_color = to_rgb_string(state.color)

        # Create ellipse centered at origin with scaled radii
        ellipse_kwargs = {
            "cx": 0,
            "cy": 0,
            "rx": state.rx,
            "ry": state.ry,
            "fill": fill_color,
        }

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            ellipse_kwargs["stroke"] = to_rgb_string(state.stroke_color)
            ellipse_kwargs["stroke_width"] = state.stroke_width

        return dw.Ellipse(**ellipse_kwargs)
