"""InfinityRenderer - renders infinity symbol as SVG paths"""

from __future__ import annotations
from typing import TYPE_CHECKING
import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.infinity import InfinityState


class InfinityRenderer(Renderer):
    """Renders infinity symbol as SVG paths"""

    def _render_core(self, state: "InfinityState", drawing=None) -> dw.Group:
        """Render infinity as an SVG path"""
        group = dw.Group()

        # Generate vertices using the state's contour generation
        contours = state._generate_contours()
        vertices = contours.outer

        if not vertices:
            return group

        # Build path from vertices
        path = dw.Path(
            fill=state.fill_color.to_hex(),
            stroke=state.stroke_color.to_hex(),
            stroke_width=state.stroke_width,
            fill_opacity=state.fill_opacity,
            stroke_opacity=state.stroke_opacity,
        )

        # Start at first vertex
        path.M(vertices[0].x, vertices[0].y)

        # Line to each subsequent vertex
        for v in vertices[1:]:
            path.L(v.x, v.y)

        # Close path if needed (infinity is closed)
        path.Z()

        group.append(path)
        return group
