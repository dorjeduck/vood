from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

from .base import State

from vood.transitions import easing
from vood.utils.colors import hex_to_color


@dataclass
class MoonPhaseState(State):
    """State class for moon phase renderers"""

    size: float = 50
    color: Tuple[int, int, int] = (255, 255, 255)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 1

    # Moon-specific properties
    illumination: float = 100  # 0-100, percentage of moon illuminated
    waxing: bool = True  # True for waxing, False for waning
    northern_hemisphere: bool = True  # True if in northern hemisphere

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "size": easing.in_out,
        "color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
        "illumination": easing.in_out,
        "waxing": easing.linear,
    }

    def __post_init__(self):
        if isinstance(self.color, str):
            self.color = hex_to_color(self.color)
        if isinstance(self.stroke_color, str):
            self.stroke_color = hex_to_color(self.stroke_color)
