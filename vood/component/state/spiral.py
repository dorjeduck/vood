from __future__ import annotations
import math
from dataclasses import dataclass

from vood.transition import easing
from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours
from vood.core.point2d import Point2D
from vood.component.registry import renderer
from vood.component.renderer.spiral import SpiralRenderer


@renderer(SpiralRenderer)
@dataclass(frozen=True)
class SpiralState(VertexState):
    """Archimedean spiral - OPEN shape"""

    start_radius: float = 5
    end_radius: float = 50
    turns: float = 3  # Number of complete rotations
    closed: bool = False

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "start_radius": easing.in_out,
        "end_radius": easing.in_out,
        "turns": easing.in_out,
    }

    def _generate_contours(self) -> VertexContours:
        """Generate spiral vertices"""
        vertices = []

        for i in range(self._num_vertices):
            t = i / (self._num_vertices - 1) if self._num_vertices > 1 else 0

            # Archimedean spiral: r = a + b*θ
            angle = t * self.turns * 2 * math.pi
            radius = self.start_radius + t * (self.end_radius - self.start_radius)

            vertices.append(Point2D(radius * math.sin(angle), -radius * math.cos(angle)))

        return VertexContours.from_single_loop(vertices, closed=self.closed)
