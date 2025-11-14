"""Triangle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

from .base import State

from vood.transitions import easing
from vood.core.color import Color, ColorInput


@dataclass(frozen=True)
class TriangleState(State):
    """State class for triangle elements"""

    size: float = 50  # Size of the triangle (distance from center to vertex)
    color: Optional[ColorInput] = (255, 0, 0)
    stroke_color: Optional[ColorInput] = None
    stroke_width: float = 0

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "size": easing.in_out,
        "color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        self._normalize_color_field("color")
        self._normalize_color_field("stroke_color")