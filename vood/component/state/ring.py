"""Ring state implementation using VertexContours"""

from __future__ import annotations
from dataclasses import dataclass

from .base import State
from .base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexCircle
from vood.component.registry import renderer
from vood.component.renderer.ring import RingRenderer
from vood.transition import easing
from vood.core.color import Color


@renderer(RingRenderer)
@dataclass(frozen=True)
class RingState(VertexState):
    """State class for ring elements (circle with circular hole)"""

    inner_radius: float = 50
    outer_radius: float = 70

    # Default easing functions for each property
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "inner_radius": easing.in_out,
        "outer_radius": easing.in_out,
    }



    def _generate_contours(self) -> VertexContours:
        """Generate ring contours with outer and inner circles

        Returns VertexContours with:
        - Outer: larger circle (counter-clockwise)
        - Hole: smaller circle (clockwise, creates the hole)
        """
        # Generate outer circle (counter-clockwise winding)
        outer_circle = VertexCircle(
            cx=0,
            cy=0,
            radius=self.outer_radius,
            num_vertices=self._num_vertices,
            start_angle=0.0,
        )

        # Generate inner circle as a hole (clockwise winding)
        # We achieve clockwise by reversing the vertices
        inner_circle = VertexCircle(
            cx=0,
            cy=0,
            radius=self.inner_radius,
            num_vertices=self._num_vertices,
            start_angle=0.0,
        )
        inner_circle_reversed = inner_circle.reverse()

        return VertexContours(outer=outer_circle, holes=[inner_circle_reversed])
