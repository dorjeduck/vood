"""Text renderer implementation for new architecture"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.text import TextState




class TextRenderer(Renderer):
    """Renderer class for rendering text elements"""

    def _render_core(
        self, state: "TextState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Text:
        fill_color = state.fill_color.to_rgb_string()
        text_kwargs = {
            "text": state.text,
            "x": 0,
            "y": 0,
            "font_family": state.font_family,
            "font_size": state.font_size,
            "font_weight": state.font_weight,
            "text_anchor": state.text_anchor,
            "letter_spacing": state.letter_spacing,
            "dominant_baseline": state.dominant_baseline,
        }
        self._set_fill_and_stroke_kwargs(state, text_kwargs, drawing)

        return dw.Text(**text_kwargs)
