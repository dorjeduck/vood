from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple

from vood.transition import easing
from .base_vertex import VertexState
from vood.component.vertex import VertexContours
from vood.component.registry import renderer
from vood.component.renderer.cross import CrossRenderer
from vood.core.point2d import Point2D


@renderer(CrossRenderer)
@dataclass(frozen=True)
class CrossState(VertexState):
    """Plus/cross shape"""

    width: float = 60  # Total width
    thickness: float = 20  # Thickness of each arm

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "width": easing.in_out,
        "thickness": easing.in_out,
    }


    def _generate_contours(self) -> VertexContours:
        """Generate cross vertices (12 corners)"""
        hw = self.width / 2
        ht = self.thickness / 2

        # Define 12 corners of the cross shape, starting from top-center, clockwise
        corners = [
            Point2D(-ht, -hw),  # 0: top of vertical bar
            Point2D(ht, -hw),  # 1
            Point2D(ht, -ht),  # 2
            Point2D(hw, -ht),  # 3: right of horizontal bar
            Point2D(hw, ht),  # 4
            Point2D(ht, ht),  # 5
            Point2D(ht, hw),  # 6: bottom of vertical bar
            Point2D(-ht, hw),  # 7
            Point2D(-ht, ht),  # 8
            Point2D(-hw, ht),  # 9: left of horizontal bar
            Point2D(-hw, -ht),  # 10
            Point2D(-ht, -ht),  # 11
        ]

        # Calculate edge lengths
        def distance(p1, p2):
            return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)

        edge_lengths = [distance(corners[i], corners[(i + 1) % 12]) for i in range(12)]
        total_perimeter = sum(edge_lengths)

        # Distribute vertices
        vertices = []
        for i in range(self._num_vertices - 1):
            target_distance = (i / (self._num_vertices - 1)) * total_perimeter

            cumulative = 0
            for edge_idx in range(12):
                if cumulative + edge_lengths[edge_idx] >= target_distance:
                    distance_along_edge = target_distance - cumulative
                    v1 = corners[edge_idx]
                    v2 = corners[(edge_idx + 1) % 12]
                    t = distance_along_edge / edge_lengths[edge_idx]

                    x = v1.x + t * (v2.x - v1.x)
                    y = v1.y + t * (v2.y - v1.y)
                    vertices.append(Point2D(x, y))
                    break
                cumulative += edge_lengths[edge_idx]

        vertices.append(vertices[0])
        return VertexContours.from_single_loop(vertices, closed=True)
