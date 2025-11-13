from __future__ import annotations
from dataclasses import dataclass

from .base import State
from .base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexCircle
from vood.transition import easing
from vood.core.color import Color


@dataclass(frozen=True)
class CircleState(VertexState):
    """State class for circle elements"""

    radius: float = 50

    # Default easing functions for each property
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "radius": easing.in_out,
    }

    @staticmethod
    def get_renderer_class():
        """Get the primitive renderer for static/keystate rendering"""
        from ..renderer.circle import CircleRenderer

        return CircleRenderer

    @staticmethod
    def get_vertex_renderer_class():
        """Get the vertex renderer for morphing transitions"""
        from ..renderer.base_vertex import VertexRenderer

        return VertexRenderer

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
