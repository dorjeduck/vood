"""Star renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


from .base import State
from vood.transitions import easing
from vood.core.color import Color


@dataclass(frozen=True)
class StarState(State):
    """State class for star elements"""

    outer_radius: float = 50  # Radius to outer points
    inner_radius: float = 20  # Radius to inner points
    points: int = 5  # Number of points (minimum 3)
    fill_color: Optional[Color] = (255, 0, 0)
    stroke_color: Optional[Color] = None
    stroke_width: float = 0

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "outer_radius": easing.in_out,
        "inner_radius": easing.in_out,
        "points": easing.linear,  # Stepped animation for integers
        "color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        self._none_color("color")
        self._none_color("stroke_color")
