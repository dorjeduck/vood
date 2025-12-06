"""Path renderer implementation for custom SVG paths (like zodiac signs)"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional


import drawsvg as dw

from vood.path.svg_path import SVGPath

from .base import Renderer

if TYPE_CHECKING:
    from ..state.path import PathState




class PathRenderer(Renderer):
    """Renderer class for rendering custom SVG path elements"""

    def _render_core(
        self, state: "PathState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Path:
        """Render the renderer's geometry with the given state

        Returns:
            drawsvg Path object
        """
        # Create path with basic properties

        path_kwargs = {
            "d": (
                state.data.to_string()
                if isinstance(state.data, SVGPath)
                else state.data
            ),
            "fill_rule": state.fill_rule,
            "stroke_dasharray": state.stroke_dasharray,
            "stroke_linecap": state.stroke_linecap,
            "stroke_linejoin": state.stroke_linejoin,
        }
        self._set_fill_and_stroke_kwargs(state, path_kwargs, drawing)


        return dw.Path(**path_kwargs)
