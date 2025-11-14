"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .base import State

from vood.transitions import easing
from vood.core.color import Color, ColorInput


@dataclass
class CircleState(State):
    """State class for circle elements"""

    radius: float = 50
    color: Optional[ColorInput] = (255, 0, 0)
    stroke_color: Optional[ColorInput] = None
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
        if self.color is not None:
            self.color = Color.from_any(self.color)
        if self.stroke_color is not None:
            self.stroke_color = Color.from_any(self.stroke_color)
