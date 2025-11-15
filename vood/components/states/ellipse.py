"""Ellipse renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .base import State

from vood.transitions import easing
from vood.core.color import Color


@dataclass(frozen=True)
class EllipseState(State):
    """State class for ellipse elements"""

    rx: float = 60  # Horizontal radius
    ry: float = 40  # Vertical radius
    fill_color: Optional[Color] = Color(0, 0, 255)
    stroke_color: Optional[Color] = Color.NONE
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
        self._none_color("color")
        self._none_color("stroke_color")
