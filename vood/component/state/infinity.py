from __future__ import annotations
import math
from dataclasses import dataclass

from vood.transition import easing
from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours
from vood.core.point2d import Point2D
from vood.component.registry import renderer
from vood.component.renderer.infinity import InfinityRenderer


@renderer(InfinityRenderer)
@dataclass(frozen=True)
class InfinityState(VertexState):
    """Infinity symbol (lemniscate)"""

    size: float = 50

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "size": easing.in_out,
    }

    def _generate_contours(self) -> VertexContours:
        """Generate infinity symbol using lemniscate parametric equations"""
        vertices = []

        for i in range(self._num_vertices - 1):
            t = (i / (self._num_vertices - 1)) * 2 * math.pi

            # Lemniscate of Bernoulli
            # x = a * cos(t) / (1 + sin²(t))
            # y = a * sin(t) * cos(t) / (1 + sin²(t))
            denominator = 1 + math.sin(t) ** 2
            x = self.size * math.cos(t) / denominator
            y = self.size * math.sin(t) * math.cos(t) / denominator

            vertices.append(Point2D(x, y))

        vertices.append(vertices[0])
        return VertexContours.from_single_loop(vertices, closed=True)
