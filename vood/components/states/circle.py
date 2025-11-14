"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .base import State

from vood.transitions import easing
from vood.core.color import Color


@dataclass(frozen=True)
class CircleState(State):
    """State class for circle elements"""

    radius: float = 50
    color: Optional[Color] = (255, 0, 0)
    stroke_color: Optional[Color] = None
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
        self._none_color("color")
        self._none_color("stroke_color")
