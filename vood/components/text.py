"""Text renderer implementation for new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

import drawsvg as dw

from vood.components import Renderer, State
from vood.utils import to_rgb_string
from vood.transitions import Easing


@dataclass
class TextState(State):
    """State class for text elements"""

    color: Tuple[int, int, int] = (0, 0, 0)
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
        "x": Easing.in_out,
        "y": Easing.in_out,
        "scale": Easing.in_out,
        "opacity": Easing.linear,
        "color": Easing.linear,
        "font_size": Easing.in_out,
        "letter_spacing": Easing.in_out,
        "text": Easing.none,
        "font_family": Easing.none,
        "text_align": Easing.none,
        "font_weight": Easing.none,
        "text_anchor": Easing.none,
        "dominant_baseline": Easing.none,
        # Stepped animation for text changes
    }


class TextRenderer(Renderer):
    """Renderer class for rendering text elements"""

    def _render_core(self, state: TextState) -> dw.Text:
        fill_color = to_rgb_string(state.color)
        text_kwargs = {
            "text": state.text,
            "x": 0,
            "y": 0,
            "font_family": state.font_family,
            "font_size": state.font_size,
            "font_weight": state.font_weight,
            "fill": fill_color,
            "text_anchor": state.text_anchor,
            "letter_spacing": state.letter_spacing,
            "dominant_baseline": state.dominant_baseline,
        }
        return dw.Text(**text_kwargs)
