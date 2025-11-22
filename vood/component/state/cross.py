from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple

from vood.transition import easing
from .base_vertex import VertexState
from vood.component.vertex import VertexContours


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
            (-ht, -hw),  # 0: top of vertical bar
            (ht, -hw),  # 1
            (ht, -ht),  # 2
            (hw, -ht),  # 3: right of horizontal bar
            (hw, ht),  # 4
            (ht, ht),  # 5
            (ht, hw),  # 6: bottom of vertical bar
            (-ht, hw),  # 7
            (-ht, ht),  # 8
            (-hw, ht),  # 9: left of horizontal bar
            (-hw, -ht),  # 10
            (-ht, -ht),  # 11
        ]

        # Calculate edge lengths
        def distance(p1, p2):
            return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

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

                    x = v1[0] + t * (v2[0] - v1[0])
                    y = v1[1] + t * (v2[1] - v1[1])
                    vertices.append((x, y))
                    break
                cumulative += edge_lengths[edge_idx]

        vertices.append(vertices[0])
        return VertexContours.from_single_loop(vertices, closed=True)
