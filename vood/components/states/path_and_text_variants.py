"""Abstract base class for renderers with multiple path variants and text labels"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional

from .base import State
from vood.transitions import easing


@dataclass
class PathAndTextVariantsState(State):
    """Base state class for multi-path renderers with text labels"""

    size: float = 500
    color: Tuple[int, int, int] = (255, 0, 0)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0

    # Text properties
    font_size: float = 35
    letter_spacing: float = 0
    font_family: str = "Comfortaa"
    text_align: str = "left"
    font_weight: str = "normal"
    text_color: Optional[Tuple[int, int, int]] = (
        None  # If None, uses same as renderer color
    )

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "size": easing.in_out,
        "color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
        "font_size": easing.in_out,
        "letter_spacing": easing.in_out,
        "font_family": easing.linear,
        "text_align": easing.linear,
        "font_weight": easing.linear,
        "text_color": easing.linear,
    }
