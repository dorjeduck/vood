from __future__ import annotations
import math
from dataclasses import dataclass

from vood.transition import easing
from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours
from vood.core.point2d import Point2D
from vood.component.registry import renderer
from vood.component.renderer.heart import HeartRenderer


@renderer(HeartRenderer)
@dataclass(frozen=True)
class HeartState(VertexState):
    """Heart shape using parametric equations"""

    size: float = 50

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "size": easing.in_out,
    }

    def _generate_contours(self) -> VertexContours:
        """Generate heart vertices using parametric equations"""
        vertices = []

        for i in range(self._num_vertices - 1):
            # Parameter t goes from 0 to 2π
            t = (i / (self._num_vertices - 1)) * 2 * math.pi

            # Heart curve parametric equations
            x = 16 * math.sin(t) ** 3
            y = -(
                13 * math.cos(t)
                - 5 * math.cos(2 * t)
                - 2 * math.cos(3 * t)
                - math.cos(4 * t)
            )

            # Scale to desired size
            scale = self.size / 20
            vertices.append(Point2D(x * scale, y * scale))

        vertices.append(vertices[0])
        return VertexContours.from_single_loop(vertices, closed=True)
