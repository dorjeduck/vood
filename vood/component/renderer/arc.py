"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from typing import Optional,TYPE_CHECKING

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from vood.component.state.arc import ArcState

class ArcRenderer(Renderer):

    def __init__(self) -> None:
        """Initialize circle renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(
        self, state: ArcState, drawing: Optional[dw.Drawing] = None
    ) -> dw.Path:
        """Render arc using SVG path primitive"""
        import math

        start_rad = math.radians(state.start_angle)
        end_rad = math.radians(state.end_angle)

        # Calculate start and end points
        start_x = state.radius * math.sin(start_rad)
        start_y = -state.radius * math.cos(start_rad)
        end_x = state.radius * math.sin(end_rad)
        end_y = -state.radius * math.cos(end_rad)

        # Determine if we need the large arc flag
        angle_diff = end_rad - start_rad
        large_arc = 1 if abs(angle_diff) > math.pi else 0

        path_kwargs = {}
        self._set_fill_and_stroke_kwargs(state, path_kwargs, drawing)
        path = dw.Path(**path_kwargs)
        
        path.M(start_x, start_y)
        path.A(state.radius, state.radius, 0, large_arc, 1, end_x, end_y)

        return path
