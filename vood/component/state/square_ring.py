"""Square ring state implementation using VertexContours"""

from __future__ import annotations
from dataclasses import dataclass

from .base import State
from .base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexSquare, rotate_vertices
from vood.component.registry import renderer
from vood.component.renderer.square_ring import SquareRingRenderer
from vood.transition import easing
from vood.core.color import Color


@renderer(SquareRingRenderer)
@dataclass(frozen=True)
class SquareRingState(VertexState):
    """State class for square ring elements (square with square hole)

    The inner square can be rotated independently using inner_rotation.
    Rotation follows vood convention: 0° = North (up), 90° = East (right)
    """

    inner_size: float = 50
    outer_size: float = 70
    inner_rotation: float = 0  # Rotation of inner square in degrees

    # Default easing functions for each property
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "inner_size": easing.in_out,
        "outer_size": easing.in_out,
        "inner_rotation": easing.in_out,
    }

    def _generate_contours(self) -> VertexContours:
        """Generate square ring contours with outer and inner squares

        Returns VertexContours with:
        - Outer: larger square (counter-clockwise)
        - Hole: smaller square (clockwise, creates the hole)

        The inner square can be rotated using inner_rotation.
        """
        # Generate outer square (counter-clockwise winding)
        outer_square = VertexSquare(
            cx=0,
            cy=0,
            size=self.outer_size,
            num_vertices=self._num_vertices,
        )

        # Generate inner square as a hole (clockwise winding)
        # We achieve clockwise by reversing the vertices
        inner_square = VertexSquare(
            cx=0,
            cy=0,
            size=self.inner_size,
            num_vertices=self._num_vertices,
        )

        # Apply rotation to inner square if specified
        if self.inner_rotation != 0:
            rotated_vertices = rotate_vertices(
                inner_square.vertices, self.inner_rotation
            )
            from vood.component.vertex import VertexLoop

            inner_square = VertexLoop(rotated_vertices, closed=True)

        inner_square_reversed = inner_square.reverse()

        return VertexContours(outer=outer_square, holes=[inner_square_reversed])
