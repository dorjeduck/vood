"""Abstract base class for renderers with multiple path variants and text labels"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import State
from vood.transition import easing

from vood.core.color import Color


@dataclass(frozen=True)
class PathAndTextVariantsState(State):
    """Base state class for multi-path renderers with text labels"""

    size: float = 500
    fill_color: Optional[Color] = Color(0, 0, 255)
    fill_opacity: float = 1
    stroke_color: Optional[Color] = Color.NONE
    stroke_opacity: float = 1
    stroke_width: float = 0

    # Text properties
    font_size: float = 35
    letter_spacing: float = 0
    font_family: str = "Comfortaa"
    text_align: str = "left"
    font_weight: str = "normal"
    text_color: Optional[Color] = Color.NONE

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "size": easing.in_out,
        "fill_color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
        "fill_opacity": easing.linear,
        "stroke_opacity": easing.linear,
        "font_size": easing.in_out,
        "letter_spacing": easing.in_out,
        "font_family": easing.linear,
        "text_align": easing.linear,
        "font_weight": easing.linear,
        "text_color": easing.linear,
    }

    def __post_init__(self):
        self._none_color("fill_color")
        self._none_color("stroke_color")
        self._none_color("text_color")