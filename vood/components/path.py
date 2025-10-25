"""Path renderer implementation for custom SVG paths (like zodiac signs)"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

import drawsvg as dw

from vood.components import Renderer, State
from vood.utils import to_rgb_string
from vood.transitions import Easing


@dataclass
class PathState(State):
    """State class for custom path elements"""

    path_data: str = "M 0,0 L 10,10 L 0,20 Z"  # Default triangle path
    color: Tuple[int, int, int] = (0, 0, 255)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0
    fill_rule: str = "evenodd"  # "evenodd" or "nonzero"

    DEFAULT_EASING = {
        "x": Easing.in_out,
        "y": Easing.in_out,
        "scale": Easing.in_out,
        "rotation": Easing.in_out,
        "opacity": Easing.linear,
        "path_data": Easing.linear,  # Stepped animation for strings
        "color": Easing.linear,
        "stroke_color": Easing.linear,
        "stroke_width": Easing.in_out,
        "fill_rule": Easing.linear,  # Stepped animation for strings
    }


class PathRenderer(Renderer):
    """Renderer class for rendering custom SVG path elements"""

    def _render_core(self, state: PathState) -> dw.Path:
        """Render the renderer's geometry with the given state

        Returns:
            drawsvg Path object
        """
        fill_color = to_rgb_string(state.color)

        # Create path with basic properties
        path_kwargs = {
            "d": state.path_data,
            "fill": fill_color,
            "fill_rule": state.fill_rule,
        }

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            path_kwargs["stroke"] = to_rgb_string(state.stroke_color)
            path_kwargs["stroke_width"] = state.stroke_width

        return dw.Path(**path_kwargs)
