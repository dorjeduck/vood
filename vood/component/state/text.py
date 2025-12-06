"""Text renderer implementation for new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from vood.component.state.base_color import ColorState

from .base import State
from vood.component.registry import renderer
from vood.component.renderer.text import TextRenderer
from vood.transition import easing
from vood.core.color import Color


@renderer(TextRenderer)
@dataclass(frozen=True)
class TextState(ColorState):
    """State class for text elements"""

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
        super().__post_init__()
        self._none_color("fill_color")
