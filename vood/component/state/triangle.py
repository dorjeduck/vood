"""Triangle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional, List

from .base_vertex import VertexState
from vood.component.vertex import VertexContours
from vood.component.registry import renderer
from vood.component.renderer.triangle import TriangleRenderer

from vood.transition import easing
from vood.core.color import Color
from vood.core.point2d import Point2D
import math


@renderer(TriangleRenderer)
@dataclass(frozen=True)
class TriangleState(VertexState):
    """State class for triangle elements"""

    size: float = 50  # Size of the triangle (distance from center to vertex)

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "size": easing.in_out,
    }

    def __post_init__(self):
        super().__post_init__()
        self._none_color("fill_color")
        self._none_color("stroke_color")


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
                Point2D(self.size * math.sin(angle), -self.size * math.cos(angle))
            )

        # Calculate perimeter lengths between vertices
        
        edge_lengths = [
            triangle_verts[i].distance_to(triangle_verts[(i + 1) % 3]) for i in range(3)
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

            x = v1.x + t * (v2.x - v1.x)
            y = v1.y + t * (v2.y - v1.y)
            vertices.append(Point2D(x, y))

        # Last vertex equals first vertex (complete the loop)
        vertices.append(vertices[0])

        return VertexContours.from_single_loop(vertices, closed=True)
