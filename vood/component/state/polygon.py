from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

from vood.transition import easing
from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours
import math


@dataclass(frozen=True)
class PolygonState(VertexState):
    """Regular polygon with n sides"""

    size: float = 50
    num_sides: int = 6

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "size": easing.in_out,
        "num_sides": easing.step,
    }

    @staticmethod
    def get_renderer_class():
        from ..renderer.polygon import PolygonRenderer

        return PolygonRenderer

    def need_morph(self, state):
        return not isinstance(state, PolygonState) or state.num_sides != self.num_sides

    def _generate_contours(self) -> VertexContours:
        """Generate regular polygon contours"""
        # Calculate corner vertices
        corners = []
        for i in range(self.num_sides):
            angle = math.radians(i * 360 / self.num_sides)
            corners.append((self.size * math.sin(angle), -self.size * math.cos(angle)))

        # Calculate edge lengths
        def distance(p1, p2):
            return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

        edge_lengths = [
            distance(corners[i], corners[(i + 1) % self.num_sides])
            for i in range(self.num_sides)
        ]
        total_perimeter = sum(edge_lengths)

        # Distribute vertices along perimeter
        vertices = []
        for i in range(self._num_vertices - 1):
            target_distance = (i / (self._num_vertices - 1)) * total_perimeter

            # Find which edge we're on
            cumulative = 0
            vertex_added = False
            for edge_idx in range(self.num_sides):
                if cumulative + edge_lengths[edge_idx] >= target_distance:
                    distance_along_edge = target_distance - cumulative
                    v1 = corners[edge_idx]
                    v2 = corners[(edge_idx + 1) % self.num_sides]
                    t = distance_along_edge / edge_lengths[edge_idx]

                    x = v1[0] + t * (v2[0] - v1[0])
                    y = v1[1] + t * (v2[1] - v1[1])
                    vertices.append((x, y))
                    vertex_added = True
                    break
                cumulative += edge_lengths[edge_idx]

            # Safety: if no vertex was added, add the last corner
            if not vertex_added:
                vertices.append(corners[-1])

        vertices.append(vertices[0])
        return VertexContours.from_single_loop(vertices, closed=True)
