"""Path renderer implementation for custom SVG paths (like zodiac signs)"""

from __future__ import annotations


import drawsvg as dw

from vood.paths.svg_path import SVGPath

from .base import Renderer
from vood.utils import to_rgb_string

from vood.components.states import PathState


class PathRenderer(Renderer):
    """Renderer class for rendering custom SVG path elements"""

    def _render_core(self, state: PathState) -> dw.Path:
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
            "fill": to_rgb_string(state.fill_color),
            "fill-rule": state.fill_rule,
            "fill-opacity": state.fill_opacity,
            "stroke": to_rgb_string(state.stroke_color),
            "stroke-width": state.stroke_width,
            "stroke-opacity": state.stroke_opacity,
            "stroke-dasharray": state.stroke_dasharray,
            "stroke-linecap": state.stroke_linecap,
            "stroke-linejoin": state.stroke_linejoin,
        }
        return dw.Path(**path_kwargs)
