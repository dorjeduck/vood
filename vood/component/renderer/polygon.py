"""Rectangle renderer implementation using new architecture"""

from __future__ import annotations
from typing import Optional

import drawsvg as dw

from .base import Renderer

from ..state.polygon import PolygonState


class PolygonRenderer(Renderer):
    """Renderer class for rendering rectangle elements"""

    def _render_core(self, state: PolygonState, drawing: Optional[dw.Drawing] = None) -> dw.Lines:
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
        lines_kwargs = {
            "close": True,
            "fill": state.fill_color.to_rgb_string(),
            "fill_opacity": state.fill_opacity,
        }

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            lines_kwargs["stroke"] = state.stroke_color.to_rgb_string()
            lines_kwargs["stroke_width"] = state.stroke_width

        return dw.Lines(*corners, **lines_kwargs)
