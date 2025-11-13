from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple

from vood.transition import easing
from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours


@dataclass(frozen=True)
class ArrowState(VertexState):

    length: float = 80
    head_width: float = 40
    head_length: float = 30
    shaft_width: float = 20
    

    closed: bool = True

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "length": easing.in_out,
        "head_width": easing.in_out,
        "head_length": easing.in_out,
        "shaft_width": easing.in_out,
    }

    def _generate_contours(self) -> VertexContours:
        """Generate arrow vertices (7 corners)"""
        hw = self.head_width / 2
        sw = self.shaft_width / 2
        hl = self.head_length
        sl = self.length - hl  # Shaft length

        # Define arrow corners, starting from back-bottom, going clockwise
        corners = [
            (-self.length / 2, -sw),  # 0: back bottom
            (-self.length / 2 + sl, -sw),  # 1: shaft bottom-right
            (-self.length / 2 + sl, -hw),  # 2: head bottom
            (self.length / 2, 0),  # 3: tip
            (-self.length / 2 + sl, hw),  # 4: head top
            (-self.length / 2 + sl, sw),  # 5: shaft top-right
            (-self.length / 2, sw),  # 6: back top
        ]

        # Calculate edge lengths
        def distance(p1, p2):
            return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

        edge_lengths = [
            distance(corners[i], corners[i + 1]) for i in range(len(corners) - 1)
        ]
        # Add closing edge (back to start)
        edge_lengths.append(distance(corners[-1], corners[0]))
        total_perimeter = sum(edge_lengths)

        # Distribute vertices
        vertices = []
        for i in range(self._num_vertices):
            t = i / (self._num_vertices - 1) if self._num_vertices > 1 else 0
            target_distance = t * total_perimeter

            cumulative = 0
            for edge_idx in range(len(corners)):
                if cumulative + edge_lengths[edge_idx] >= target_distance:
                    distance_along_edge = target_distance - cumulative
                    v1 = corners[edge_idx]
                    v2 = corners[(edge_idx + 1) % len(corners)]
                    edge_t = distance_along_edge / edge_lengths[edge_idx]

                    x = v1[0] + edge_t * (v2[0] - v1[0])
                    y = v1[1] + edge_t * (v2[1] - v1[1])
                    vertices.append((x, y))
                    break
                cumulative += edge_lengths[edge_idx]

        return VertexContours.from_single_loop(vertices, closed=self.closed)
