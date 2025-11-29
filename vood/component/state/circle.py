from __future__ import annotations
from dataclasses import dataclass

from .base import State
from .base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexCircle
from vood.component.registry import renderer
from vood.component.renderer.circle import CircleRenderer
from vood.transition import easing


@renderer(CircleRenderer)
@dataclass(frozen=True)
class CircleState(VertexState):
    """State class for circle elements"""

    radius: float = 50

    # Default easing functions for each property
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "radius": easing.in_out,
    }



    def _generate_contours(self) -> VertexContours:
        """Generate circle contours

        Returns VertexContours with a single circular outer contour, no holes.
        """
        circle = VertexCircle(
            cx=0,
            cy=0,
            radius=self.radius,
            num_vertices=self._num_vertices,
            start_angle=0.0,
        )

        return VertexContours(outer=circle, holes=None)
