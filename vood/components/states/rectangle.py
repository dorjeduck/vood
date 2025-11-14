"""Rectangle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .base import State

from vood.transitions import easing
from vood.core.color import Color, ColorInput


@dataclass(frozen=True)
class RectangleState(State):
    """State class for rectangle elements"""

    width: float = 100
    height: float = 60
    color: Optional[ColorInput] = (255, 0, 0)
    stroke_color: Optional[ColorInput] = None
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
        self._normalize_color_field("color")
        self._normalize_color_field("stroke_color")