"""Triangle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional, List

from .base_vertex import VertexState
from vood.component.vertex import VertexContours

from vood.transition import easing
from vood.core.color import Color

import math


@dataclass(frozen=True)
class TriangleState(VertexState):
    """State class for triangle elements"""

    size: float = 50  # Size of the triangle (distance from center to vertex)

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "size": easing.in_out,
    }

    def __post_init__(self):
        self._none_color("fill_color")
        self._none_color("stroke_color")

    @staticmethod
    def get_renderer_class():
        from ..renderer.triangle import TriangleRenderer

        return TriangleRenderer

    def _generate_contours(self) -> VertexContours:
        """Generate triangle vertices distributed along perimeter

        Triangle points upward with vertices at:
        - Top: 0° (North/straight up)
        - Bottom-right: 120°
        - Bottom-left: 240°

        Generates num_points vertices that form a complete closed loop.
        The last vertex equals the first vertex to properly close the shape.
        """
        # Calculate triangle vertices (pointing up, Vood coordinate system)
        triangle_verts = []
        for i in range(3):
            angle = math.radians(i * 120)  # 0°, 120°, 240°
            triangle_verts.append(
                (self.size * math.sin(angle), -self.size * math.cos(angle))
            )

        # Calculate perimeter lengths between vertices
        def distance(p1, p2):
            return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

        edge_lengths = [
            distance(triangle_verts[i], triangle_verts[(i + 1) % 3]) for i in range(3)
        ]
        total_perimeter = sum(edge_lengths)

        # Distribute num_points - 1 vertices along the perimeter
        vertices = []

        for i in range(self._num_vertices - 1):
            target_distance = (i / (self._num_vertices - 1)) * total_perimeter

            # Find which edge we're on
            cumulative = 0
            for edge_idx in range(3):
                if cumulative + edge_lengths[edge_idx] >= target_distance:
                    current_edge = edge_idx
                    distance_along_edge = target_distance - cumulative
                    break
                cumulative += edge_lengths[edge_idx]

            # Interpolate along current edge
            v1 = triangle_verts[current_edge]
            v2 = triangle_verts[(current_edge + 1) % 3]
            t = distance_along_edge / edge_lengths[current_edge]

            x = v1[0] + t * (v2[0] - v1[0])
            y = v1[1] + t * (v2[1] - v1[1])
            vertices.append((x, y))

        # Last vertex equals first vertex (complete the loop)
        vertices.append(vertices[0])

        return VertexContours.from_single_loop(vertices, closed=True)
