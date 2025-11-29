from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple

from vood.transition import easing
from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours
from vood.core.point2d import Point2D
from vood.component.registry import renderer
from vood.component.renderer.arrow import ArrowRenderer


@renderer(ArrowRenderer)
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
            Point2D(-self.length / 2, -sw),  # 0: back bottom
            Point2D(-self.length / 2 + sl, -sw),  # 1: shaft bottom-right
            Point2D(-self.length / 2 + sl, -hw),  # 2: head bottom
            Point2D(self.length / 2, 0),  # 3: tip
            Point2D(-self.length / 2 + sl, hw),  # 4: head top
            Point2D(-self.length / 2 + sl, sw),  # 5: shaft top-right
            Point2D(-self.length / 2, sw),  # 6: back top
        ]

        edge_lengths = [
            corners[i].distance_to(corners[i + 1]) for i in range(len(corners) - 1)
        ]
  
        # Add closing edge (back to start)
        edge_lengths.append(corners[-1].distance_to(corners[0]))
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

                    x = v1.x + edge_t * (v2.x - v1.x)
                    y = v1.y + edge_t * (v2.y - v1.y)
                    vertices.append(Point2D(x, y))
                    break
                cumulative += edge_lengths[edge_idx]

        return VertexContours.from_single_loop(vertices, closed=self.closed)
