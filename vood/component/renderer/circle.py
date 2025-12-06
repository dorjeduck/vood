"""Circle renderer implementation using new architecture"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.circle import CircleState



class CircleRenderer(Renderer):
    """Renderer class for rendering circle elements

    The radius is now part of the state, making it animatable!
    """

    def __init__(self) -> None:
        """Initialize circle renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(
        self, state: "CircleState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Circle:
        """Render the core circle geometry centered at origin (0,0)"""
        circle_kwargs = {
            "cx": 0,
            "cy": 0,
            "r": state.radius,
        }
        self._set_fill_and_stroke_kwargs(state, circle_kwargs, drawing)

        return dw.Circle(**circle_kwargs)
