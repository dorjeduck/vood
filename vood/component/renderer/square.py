"""Rectangle renderer implementation using new architecture"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.square import SquareState




class SquareRenderer(Renderer):
    """Renderer class for rendering rectangle elements"""

    def _render_core(
        self, state: "SquareState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Rectangle:
        """Render the rectangle renderer (geometry only, no transforms)

        Args:
            state (RectangleState): The state of the rectangle

        Returns:
            dw.Rectangle: The drawsvg rectangle object
        """


        # Create rectangle centered at origin with scaled dimensions
        rect_kwargs = {
            "x": -(state.size) / 2,  # Center the rectangle
            "y": -(state.size) / 2,
            "width": state.size,
            "height": state.size,
        }

        self._set_fill_and_stroke_kwargs(state, rect_kwargs, drawing)

        return dw.Rectangle(**rect_kwargs)
