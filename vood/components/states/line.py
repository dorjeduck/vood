"""Line renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import  Optional


from .base import State

from vood.transitions import easing
from vood.core.color import Color, ColorInput


@dataclass
class LineState(State):
    """State class for line elements"""

    length: float = 100  # Length of the line
    stroke_color: Optional[ColorInput] = (220, 220, 220)
    stroke_width: float = 1
    stroke_dasharray: Optional[str] = None  # For dashed lines, e.g., "5,5"
    stroke_linecap: str = "round"  # "butt", "round", "square"

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "length": easing.in_out,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
        "stroke_dasharray": easing.linear,  # Stepped animation for strings
        "stroke_linecap": easing.linear,  # Stepped animation for strings
    }

    def __post_init__(self):
        if self.stroke_color is not None:
            self.stroke_color = Color.from_any(self.stroke_color)
