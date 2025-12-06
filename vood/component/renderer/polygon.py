"""Rectangle renderer implementation using new architecture"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.polygon import PolygonState




class PolygonRenderer(Renderer):
    """Renderer class for rendering rectangle elements"""

    def _render_core(
        self, state: "PolygonState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Lines:
        """Render regular polygon using SVG primitive

        Args:
            state (MorphPolygonState): The state of the polygon

        Returns:
            dw.Lines: The drawsvg lines object forming a closed polygon
        """
        import math

        # Generate corner points only
        corners = []
        for i in range(state.num_sides):
            angle = (i / state.num_sides) * 2 * math.pi - math.pi / 2
            x = state.size * math.cos(angle)
            y = state.size * math.sin(angle)
            corners.extend([x, y])

        # Build kwargs
        lines_kwargs = {"close": True}
        self._set_fill_and_stroke_kwargs(state, lines_kwargs, drawing)


        return dw.Lines(*corners, **lines_kwargs)
