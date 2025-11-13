"""Astroid renderer - SVG primitive-based for static/keystate rendering"""

from __future__ import annotations
from typing import Optional
import drawsvg as dw
import math

from .base import Renderer
from ..state.astroid import AstroidState


class AstroidRenderer(Renderer):
    """Renderer for astroid elements using SVG primitives

    Renders an astroid - a star-like shape with pointed cusps connected
    by inward-bending curves. Uses quadratic Bezier curves for smooth,
    high-quality rendering.

    This is used for static rendering and at keystate endpoints (t=0, t=1).
    During morphing (0 < t < 1), the VertexRenderer is used instead to enable
    smooth transitions between different shapes.
    """

    def _render_core(self, state: AstroidState, drawing: Optional[dw.Drawing] = None) -> dw.Group:
        """Render astroid using SVG path primitives with quadratic Bezier curves"""

        group = dw.Group()

        # Create a path for the astroid shape
        path = dw.Path(
            fill=state.fill_color.to_rgb_string() if state.fill_color else "none",
            fill_opacity=state.fill_opacity,
            stroke=state.stroke_color.to_rgb_string() if state.stroke_color and state.stroke_width > 0 else "none",
            stroke_width=state.stroke_width if state.stroke_color and state.stroke_width > 0 else 0,
            stroke_opacity=state.stroke_opacity if state.stroke_color and state.stroke_width > 0 else 0,
            stroke_linejoin='round',
            stroke_linecap='round'
        )

        # Calculate cusp positions (the pointed tips)
        cusps = []
        for i in range(state.num_cusps):
            angle = math.radians(i * (360 / state.num_cusps) - 90)  # -90 to start at top
            x = state.radius * math.cos(angle)
            y = state.radius * math.sin(angle)
            cusps.append((x, y))

        # Start at first cusp
        path.M(*cusps[0])

        # Draw curves connecting cusps
        for i in range(state.num_cusps):
            start_cusp = cusps[i]
            end_cusp = cusps[(i + 1) % state.num_cusps]

            # Calculate control point for inward-bending curve
            # Midpoint between cusps
            mid_x = (start_cusp[0] + end_cusp[0]) / 2
            mid_y = (start_cusp[1] + end_cusp[1]) / 2

            # Pull control point toward center based on curvature
            control_x = mid_x * (1 - state.curvature)
            control_y = mid_y * (1 - state.curvature)

            # Draw quadratic Bezier curve to next cusp
            path.Q(control_x, control_y, *end_cusp)

        path.Z()
        group.append(path)
        return group
