from __future__ import annotations
from typing import Optional

import drawsvg as dw

from .base import Renderer

from ..state.cross import CrossState


class CrossRenderer(Renderer):
    """Renderer class for rendering cross elements"""

    def __init__(self) -> None:
        """Initialize circle renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(self, state: CrossState, drawing: Optional[dw.Drawing] = None) -> dw.Lines:
        """Render cross using SVG polygon primitive"""
        hw = state.width / 2
        ht = state.thickness / 2

        # Just the 12 corner points
        corners = [
            -ht,
            -hw,  # 0: top of vertical bar
            ht,
            -hw,  # 1
            ht,
            -ht,  # 2
            hw,
            -ht,  # 3: right of horizontal bar
            hw,
            ht,  # 4
            ht,
            ht,  # 5
            ht,
            hw,  # 6: bottom of vertical bar
            -ht,
            hw,  # 7
            -ht,
            ht,  # 8
            -hw,
            ht,  # 9: left of horizontal bar
            -hw,
            -ht,  # 10
            -ht,
            -ht,  # 11
        ]

        cross_kwargs = {
            "stroke": state.stroke_color.to_rgb_string(),
            "stroke_width": state.stroke_width,
            "stroke_opacity": state.stroke_opacity,
            "fill": state.fill_color.to_rgb_string(),
            "fill_opacity": state.fill_opacity,
        }

        return dw.Lines(*corners, close=True, **cross_kwargs)
