"""Ring renderer - SVG primitive-based for static/keystate rendering"""

from __future__ import annotations
from typing import Optional
import drawsvg as dw

from .base import Renderer
from ..state.ring import RingState


class RingRenderer(Renderer):
    """Renderer for ring elements using SVG primitives

    Uses evenodd fill-rule with SVG arcs for clean, high-quality rendering.
    This is used for static rendering and at keystate endpoints (t=0, t=1).

    During morphing (0 < t < 1), the VertexRenderer is used instead to enable
    smooth transitions between different shapes.
    """

    def _render_core(self, state: RingState, drawing: Optional[dw.Drawing] = None) -> dw.Group:
        """Render ring using SVG arc primitives with evenodd fill-rule"""
        group = dw.Group()

        # Create a path that defines the ring shape using even-odd fill rule
        path = dw.Path(
            fill=state.fill_color.to_rgb_string() if state.fill_color else "none",
            fill_opacity=state.fill_opacity,
            fill_rule="evenodd",
            stroke=state.stroke_color.to_rgb_string() if state.stroke_color and state.stroke_width > 0 else "none",
            stroke_width=state.stroke_width if state.stroke_color and state.stroke_width > 0 else 0,
            stroke_opacity=state.stroke_opacity if state.stroke_color and state.stroke_width > 0 else 0,
            stroke_linejoin='round',
            stroke_linecap='round'
        )

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
