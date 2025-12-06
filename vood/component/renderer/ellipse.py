"""Ellipse renderer implementation using new architecture"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.ellipse import EllipseState



class EllipseRenderer(Renderer):
    """Renderer class for rendering ellipse elements"""

    def __init__(self) -> None:
        """Initialize ellipse renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(
        self, state: "EllipseState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Ellipse:
        """Render the ellipse renderer (geometry only) with the given state

        Returns:
            drawsvg Ellipse object
        """

        # Create ellipse centered at origin with scaled radii
        ellipse_kwargs = {
            "cx": 0,
            "cy": 0,
            "rx": state.rx,
            "ry": state.ry,
        }

        self._set_fill_and_stroke_kwargs(state, ellipse_kwargs, drawing)

        return dw.Ellipse(**ellipse_kwargs)
