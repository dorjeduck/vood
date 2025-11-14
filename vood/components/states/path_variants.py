"""Abstract base class for renderers with multiple path variants"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .base import State
from vood.transitions import easing
from vood.core.color import Color, ColorInput

@dataclass
class PathVariantsState(State):
    """Base state class for multi-path renderers"""

    size: float = 50
    color: Optional[ColorInput] = (255, 0, 0)
    stroke_color: Optional[ColorInput] = None
    stroke_width: float = 0
    case_sensitive: bool = False

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "size": easing.in_out,
        "color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        if self.color is not None:
            self.color = Color.from_any(self.color)
        if self.stroke_color is not None:
            self.stroke_color = Color.from_any(self.stroke_color)
