"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

from .base import State

from vood.transitions import easing

from vood.utils import to_rgb_string
from vood.utils.colors import hex_to_color


@dataclass
class CircleState(State):
    """State class for circle elements"""

    radius: float = 50
    color: Optional[Tuple[int, int, int]] = (255, 0, 0)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0

    # Default easing functions for each property
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "radius": easing.in_out,
        "color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        if isinstance(self.color, str):
            self.color = hex_to_color(self.color)
        if isinstance(self.stroke_color, str):
            self.stroke_color = hex_to_color(self.stroke_color)
