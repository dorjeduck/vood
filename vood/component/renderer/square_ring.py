"""Square ring renderer - SVG primitive-based for static/keystate rendering"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.square_ring import SquareRingState

from vood.core.point2d import Point2D


class SquareRingRenderer(Renderer):
    """Renderer for square ring elements using SVG primitives

    Uses evenodd fill-rule with SVG paths for clean, high-quality rendering.
    This is used for static rendering and at keystate endpoints (t=0, t=1).

    During morphing (0 < t < 1), the VertexRenderer is used instead to enable
    smooth transitions between different shapes.
    """

    def _render_core(
        self, state: "SquareRingState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Group:
        """Render square ring using SVG path primitives with evenodd fill-rule"""
        import math

        group = dw.Group()

        # Create a path that defines the square ring shape using even-odd fill rule
        path_kwargs = {
            "fill_rule": "evenodd",
            "stroke_linejoin": "round",
            "stroke_linecap": "round",
        }
        self._set_fill_and_stroke_kwargs(state, path_kwargs, drawing)

        path = dw.Path(**path_kwargs)
        # Calculate half sizes for positioning
        outer_half = state.outer_size / 2
        inner_half = state.inner_size / 2

        # Draw outer square (clockwise)
        path.M(-outer_half, -outer_half)  # Top-left
        path.L(outer_half, -outer_half)  # Top-right
        path.L(outer_half, outer_half)  # Bottom-right
        path.L(-outer_half, outer_half)  # Bottom-left
        path.Z()  # Close path

        # Draw inner square (counter-clockwise - creates the hole due to even-odd rule)
        # Apply rotation if specified
        if state.inner_rotation != 0:
            # Convert rotation to radians
            angle_rad = math.radians(state.inner_rotation)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Define corners and rotate them
            corners = [
                (-inner_half, -inner_half),  # Top-left
                (-inner_half, inner_half),  # Bottom-left
                (inner_half, inner_half),  # Bottom-right
                (inner_half, -inner_half),  # Top-right
            ]

            rotated_corners = [
                Point2D(x * cos_a - y * sin_a, x * sin_a + y * cos_a)
                for x, y in corners
            ]

            path.M(rotated_corners[0].x, rotated_corners[0].y)
            for corner in rotated_corners[1:]:
                path.L(corner.x, corner.y)
            path.Z()
        else:
            # No rotation - use simple coordinates
            path.M(-inner_half, -inner_half)  # Top-left
            path.L(-inner_half, inner_half)  # Bottom-left (reversed direction)
            path.L(inner_half, inner_half)  # Bottom-right
            path.L(inner_half, -inner_half)  # Top-right
            path.Z()  # Close path

        group.append(path)
        return group
