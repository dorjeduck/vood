"""Ellipse renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

from .base import State

from vood.transitions import easing
from vood.utils.colors import hex_to_color


@dataclass
class EllipseState(State):
    """State class for ellipse elements"""

    rx: float = 60  # Horizontal radius
    ry: float = 40  # Vertical radius
    color: Tuple[int, int, int] = (0, 0, 255)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "rx": easing.in_out,
        "ry": easing.in_out,
        "color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        if isinstance(self.color, str):
            self.color = hex_to_color(self.color)
        if isinstance(self.stroke_color, str):
            self.stroke_color = hex_to_color(self.stroke_color)
