"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from typing import Optional

import drawsvg as dw

from .base import Renderer

from ..state.arrow import ArrowState


class ArrowRenderer(Renderer):
    """Renderer class for rendering circle elements

    The radius is now part of the state, making it animatable!
    """

    def __init__(self) -> None:
        """Initialize circle renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(self, state: ArrowState, drawing: Optional[dw.Drawing] = None) -> dw.Lines:
        """Render arrow using SVG polygon primitive"""
        hw = state.head_width / 2
        sw = state.shaft_width / 2
        hl = state.head_length
        sl = state.length - hl

        # Just the 7 corner points
        corners = [
            -state.length / 2,
            -sw,  # back bottom
            -state.length / 2 + sl,
            -sw,  # shaft bottom-right
            -state.length / 2 + sl,
            -hw,  # head bottom
            state.length / 2,
            0,  # tip
            -state.length / 2 + sl,
            hw,  # head top
            -state.length / 2 + sl,
            sw,  # shaft top-right
            -state.length / 2,
            sw,  # back top
        ]

        arrow_kwargs = {
            "stroke": state.stroke_color.to_rgb_string(),
            "stroke_width": state.stroke_width,
            "stroke_opacity": state.stroke_opacity,
            "fill": state.fill_color.to_rgb_string(),
            "fill_opacity": state.fill_opacity,
        }

        return dw.Lines(*corners, close=True, **arrow_kwargs)
