"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from typing import Optional,TYPE_CHECKING

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from vood.component.state.arrow import ArrowState


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

        arrow_kwargs = {}
        self._set_fill_and_stroke_kwargs(state, arrow_kwargs, drawing)


        return dw.Lines(*corners, close=True, **arrow_kwargs)
