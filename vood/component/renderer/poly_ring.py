"""Polygon ring renderer - SVG primitive-based for static/keystate rendering"""

from __future__ import annotations
from typing import Optional
import drawsvg as dw
import math

from .base import Renderer
from ..state.poly_ring import PolyRingState


class PolyRingRenderer(Renderer):
    """Renderer for polygon ring elements using SVG primitives

    Uses evenodd fill-rule with SVG paths for clean, high-quality rendering.
    This is used for static rendering and at keystate endpoints (t=0, t=1).

    During morphing (0 < t < 1), the VertexRenderer is used instead to enable
    smooth transitions between different shapes.
    """

    def _render_core(self, state: PolyRingState, drawing: Optional[dw.Drawing] = None) -> dw.Group:
        """Render polygon ring using SVG path primitives with evenodd fill-rule"""

        group = dw.Group()

        # Create a path that defines the polygon ring shape using even-odd fill rule
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

        # Generate outer polygon vertices (clockwise)
        outer_vertices = self._generate_polygon_vertices(
            size=state.outer_size,
            num_edges=state.num_edges,
            rotation=0
        )

        # Draw outer polygon
        path.M(*outer_vertices[0])
        for vertex in outer_vertices[1:]:
            path.L(*vertex)
        path.Z()

        # Generate inner polygon vertices (counter-clockwise - creates the hole due to even-odd rule)
        inner_vertices = self._generate_polygon_vertices(
            size=state.inner_size,
            num_edges=state.num_edges,
            rotation=state.inner_rotation
        )

        # Draw inner polygon (reversed direction for hole)
        path.M(*inner_vertices[0])
        for vertex in reversed(inner_vertices[1:]):
            path.L(*vertex)
        path.Z()

        group.append(path)
        return group

    def _generate_polygon_vertices(self, size: float, num_edges: int, rotation: float = 0) -> list[tuple[float, float]]:
        """Generate vertices for a regular polygon

        Args:
            size: Distance from center to vertices (circumradius)
            num_edges: Number of polygon edges
            rotation: Rotation in degrees (0° = North, 90° = East)

        Returns:
            List of (x, y) vertex coordinates
        """
        vertices = []
        angle_step = 360.0 / num_edges

        for i in range(num_edges):
            # Start at North (270° in standard coords) and go clockwise
            # Vood convention: 0° = North, 90° = East
            angle = -90 + rotation + (i * angle_step)  # -90 to start at North
            angle_rad = math.radians(angle)

            x = size * math.cos(angle_rad)
            y = size * math.sin(angle_rad)
            vertices.append((x, y))

        return vertices
