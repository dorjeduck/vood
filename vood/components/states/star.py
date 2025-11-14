"""Star renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import  Optional


from .base import State
from vood.transitions import easing
from vood.core.color import Color, ColorInput


@dataclass
class StarState(State):
    """State class for star elements"""

    outer_radius: float = 50  # Radius to outer points
    inner_radius: float = 20  # Radius to inner points
    points: int = 5  # Number of points (minimum 3)
    color: Optional[ColorInput] = (255, 0, 0)
    stroke_color: Optional[ColorInput] = None
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
        if self.color is not None:
            self.color = Color.from_any(self.color)
        if self.stroke_color is not None:
            self.stroke_color = Color.from_any(self.stroke_color)
