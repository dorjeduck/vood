"""Rectangle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

from .base import State

from vood.transitions import easing
from vood.utils.colors import hex_to_color


@dataclass
class RectangleState(State):
    """State class for rectangle elements"""

    width: float = 100
    height: float = 60
    color: Tuple[int, int, int] = (0, 255, 0)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0
    corner_radius: float = 0  # For rounded rectangles

    # Default easing functions for each property
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "width": easing.in_out,
        "height": easing.in_out,
        "color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
        "corner_radius": easing.in_out,
        "rotation": easing.in_out,
    }

    def __post_init__(self):
        if isinstance(self.color, str):
            self.color = hex_to_color(self.color)
        if isinstance(self.stroke_color, str):
            self.stroke_color = hex_to_color(self.stroke_color)
