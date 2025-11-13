"""Perforated polygon state - regular polygon with holes"""

from __future__ import annotations
from dataclasses import dataclass

from .base import PerforatedVertexState
from vood.component.state.base import State
from vood.component.vertex import VertexRegularPolygon, VertexLoop
from vood.transition import easing


@dataclass(frozen=True)
class PerforatedPolygonState(PerforatedVertexState):
    """Regular polygon with holes

    A regular polygon outer shape with zero or more holes of arbitrary shapes.

    Args:
        num_sides: Number of sides (3 = triangle, 5 = pentagon, 6 = hexagon, etc.)
        size: Radius of circumscribed circle
        holes: List of Shape objects specifying hole geometry and positions

    Example:
        PerforatedPolygonState(
            num_sides=6,
            size=100,
            holes=[Circle(radius=30, x=0, y=0)],
            fill_color=Color("#3498DB"),
        )
    """

    num_sides: int = 6
    size: float = 100

    DEFAULT_EASING = {
        **PerforatedVertexState.DEFAULT_EASING,
        "num_sides": easing.step,  # Integer, step interpolation
        "size": easing.in_out,
    }

    def _generate_outer_contour(self) -> VertexLoop:
        """Generate regular polygon outer contour"""
        return VertexRegularPolygon(
            cx=0, cy=0,
            size=self.size,
            num_sides=self.num_sides,
            num_vertices=self._num_vertices,
            rotation=0
        )
