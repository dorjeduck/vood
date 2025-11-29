from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple

from vood.transition import easing
from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours

from vood.core.point2d import Point2D


@dataclass(frozen=True)
class FlowerState(VertexState):
    """Flower with n petals using rose curve"""

    size: float = 50
    num_petals: int = 5

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "size": easing.in_out,
        "num_petals": easing.step,
    }

    def _generate_contours(self) -> VertexContours:
        """Generate flower vertices using rose curve: r = a * cos(k*θ)"""
        vertices = []

        # For odd petals: k = n, range 0 to π
        # For even petals: k = n, range 0 to 2π
        angle_range = math.pi if self.num_petals % 2 == 1 else 2 * math.pi

        for i in range(self._num_vertices - 1):
            t = (i / (self._num_vertices - 1)) * angle_range

            # Rose curve
            r = abs(self.size * math.cos(self.num_petals * t))

            vertices.append(Point2D(r * math.sin(t), -r * math.cos(t)))

        vertices.append(vertices[0])
        return VertexContours.from_single_loop(vertices, closed=True)
