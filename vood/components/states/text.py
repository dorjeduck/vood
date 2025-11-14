"""Text renderer implementation for new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .base import State
from vood.transitions import easing
from vood.core.color import Color, ColorInput


@dataclass
class TextState(State):
    """State class for text elements"""

    color: Optional[ColorInput] = (255, 0, 0)
    font_size: float = 16

    letter_spacing: float = 0  # Additional spacing between letters

    text: str = ""
    font_family: str = "Arial"
    text_align: str = "middle"
    font_weight: str = "normal"
    text_anchor: str = "middle"
    dominant_baseline: str = "central"

    # Default easing functions for each property
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "color": easing.linear,
        "font_size": easing.in_out,
        "letter_spacing": easing.in_out,
        "text": easing.step,
        "font_family": easing.step,
        "text_align": easing.step,
        "font_weight": easing.step,
        "text_anchor": easing.step,
        "dominant_baseline": easing.step,
        # Stepped animation for text changes
    }

    def __post_init__(self):
        self.color = self._normalize_color(self.color)
