from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

from .base import State

from vood.transitions import easing
from vood.core.color import Color


@dataclass(frozen=True)
class MoonPhaseState(State):
    """State class for moon phase renderers"""

    size: float = 50
    fill_color: Optional[Color] = Color(255, 0, 0)
    stroke_color: Optional[Color] = Color.NONE
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
        self._none_color("color")
        self._none_color("stroke_color")
