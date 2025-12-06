"""WaveRenderer - renders wave shapes as SVG paths"""

from __future__ import annotations
from typing import TYPE_CHECKING
import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.wave import WaveState


class WaveRenderer(Renderer):
    """Renders wave shapes as SVG paths"""

    def _render_core(self, state: "WaveState", drawing=None) -> dw.Group:
        """Render wave as an SVG path"""
        group = dw.Group()

        # Generate vertices using the state's contour generation
        contours = state._generate_contours()
        vertices = contours.outer

        if not vertices:
            return group

        # Build path from vertices
        path_kwargs = {}
        self._set_fill_and_stroke_kwargs(state, path_kwargs, drawing)
        path = dw.Path(**path_kwargs)
        
        # Start at first vertex
        path.M(vertices[0].x, vertices[0].y)

        # Line to each subsequent vertex
        for v in vertices[1:]:
            path.L(v.x, v.y)

        # Close path if needed
        if state.closed:
            path.Z()

        group.append(path)
        return group
