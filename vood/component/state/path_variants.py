"""Abstract base class for renderers with multiple path variants"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .base import State
from vood.transition import easing
from vood.core.color import Color


@dataclass(frozen=True)
class PathVariantsState(State):
    """Base state class for multi-path renderers"""

    size: float = 50
    fill_color: Optional[Color] = Color(0, 0, 255)
    fill_opacity: float = 1
    stroke_color: Optional[Color] = Color.NONE
    stroke_opacity: float = 1
    stroke_width: float = 0
    case_sensitive: bool = False

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "size": easing.in_out,
        "fill_color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
        "fill_opacity": easing.linear,
        "stroke_opacity": easing.linear,
    }

    def __post_init__(self):
        self._none_color("fill_color")
        self._none_color("stroke_color")

