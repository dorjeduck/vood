"""Polygon ring state implementation using VertexContours"""

from __future__ import annotations
from dataclasses import dataclass

from .base import State
from .base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexRegularPolygon
from vood.transition import easing
from vood.core.color import Color


@dataclass(frozen=True)
class PolyRingState(VertexState):
    """State class for polygon ring elements (polygon with polygon hole)

    A generic ring shape with customizable number of edges for both
    the outer and inner polygons. The inner polygon can be rotated
    independently using inner_rotation. Use the base rotation parameter
    to rotate the entire shape.

    Rotation follows vood convention: 0° = North (up), 90° = East (right)
    """

    inner_size: float = 50
    outer_size: float = 70
    num_edges: int = 6  # Number of edges (3=triangle, 4=square, 5=pentagon, etc.)
    inner_rotation: float = 0  # Rotation of inner polygon in degrees

    # Default easing functions for each property
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "inner_size": easing.in_out,
        "outer_size": easing.in_out,
        "num_edges": easing.step,  # Discrete values, no smooth interpolation
        "inner_rotation": easing.in_out,
    }

    @staticmethod
    def get_renderer_class():
        """Get the primitive renderer for static/keystate rendering"""
        from ..renderer.poly_ring import PolyRingRenderer

        return PolyRingRenderer

    def _generate_contours(self) -> VertexContours:
        """Generate polygon ring contours with outer and inner polygons

        Returns VertexContours with:
        - Outer: larger polygon (counter-clockwise)
        - Hole: smaller polygon (clockwise, creates the hole)

        The inner polygon can be rotated independently using inner_rotation.
        """
        # Generate outer polygon (counter-clockwise winding)
        outer_polygon = VertexRegularPolygon(
            cx=0,
            cy=0,
            size=self.outer_size,
            num_sides=self.num_edges,
            num_vertices=self._num_vertices,
            rotation=0
        )

        # Generate inner polygon as a hole (clockwise winding)
        # We achieve clockwise by reversing the vertices
        inner_polygon = VertexRegularPolygon(
            cx=0,
            cy=0,
            size=self.inner_size,
            num_sides=self.num_edges,
            num_vertices=self._num_vertices,
            rotation=self.inner_rotation
        )

        inner_polygon_reversed = inner_polygon.reverse()

        return VertexContours(outer=outer_polygon, holes=[inner_polygon_reversed])
