"""Star renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional


from .base import State
from vood.transitions import easing
from vood.utils.colors import hex_to_color


@dataclass
class StarState(State):
    """State class for star elements"""

    outer_radius: float = 50  # Radius to outer points
    inner_radius: float = 20  # Radius to inner points
    points: int = 5  # Number of points (minimum 3)
    color: Tuple[int, int, int] = (255, 215, 0)  # Gold color
    stroke_color: Optional[Tuple[int, int, int]] = None
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
        if isinstance(self.color, str):
            self.color = hex_to_color(self.color)
        if isinstance(self.stroke_color, str):
            self.stroke_color = hex_to_color(self.stroke_color)
