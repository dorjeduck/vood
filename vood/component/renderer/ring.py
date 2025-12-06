"""Ring renderer - SVG primitive-based for static/keystate rendering"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.ring import RingState



class RingRenderer(Renderer):
    """Renderer for ring elements using SVG primitives

    Uses evenodd fill-rule with SVG arcs for clean, high-quality rendering.
    This is used for static rendering and at keystate endpoints (t=0, t=1).

    During morphing (0 < t < 1), the VertexRenderer is used instead to enable
    smooth transitions between different shapes.
    """

    def _render_core(
        self, state: "RingState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Group:
        """Render ring using SVG arc primitives with evenodd fill-rule"""
        group = dw.Group()

        # Create a path that defines the ring shape using even-odd fill rule
        path_kwargs = {
            "fill_rule": "evenodd",
            "stroke_linejoin": "round",
            "stroke_linecap": "round",
        }
        self._set_fill_and_stroke_kwargs(state, path_kwargs, drawing)

        path = dw.Path(**path_kwargs)

        # Draw outer circle (clockwise)
        path.M(state.outer_radius, 0)
        path.A(state.outer_radius, state.outer_radius, 0, 0, 1, -state.outer_radius, 0)
        path.A(state.outer_radius, state.outer_radius, 0, 0, 1, state.outer_radius, 0)

        # Draw inner circle (counter-clockwise - creates the hole due to even-odd rule)
        path.M(state.inner_radius, 0)
        path.A(state.inner_radius, state.inner_radius, 0, 0, 0, -state.inner_radius, 0)
        path.A(state.inner_radius, state.inner_radius, 0, 0, 0, state.inner_radius, 0)

        group.append(path)
        return group
