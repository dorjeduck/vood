"""Perforated triangle state - triangle with  holes"""

from __future__ import annotations
from dataclasses import dataclass

from .base import PerforatedVertexState
from vood.component.state.base import State
from vood.component.vertex import VertexTriangle, VertexLoop
from vood.transition import easing


@dataclass(frozen=True)
class PerforatedTriangleState(PerforatedVertexState):
    """Triangle with  holes

    A triangular outer shape with zero or more vertex loops of arbitrary shapes.

    Args:
        size: Size of the triangle (distance from center to vertices)
         holes : List of Shape objects specifying hole geometry and positions

    Example:
        PerforatedTriangleState(
            size=100,
             holes =[Circle(radius=20, x=0, y=10)],
            fill_color=Color("#2ECC71"),
        )
    """

    size: float = 100

    DEFAULT_EASING = {
        **PerforatedVertexState.DEFAULT_EASING,
        "size": easing.in_out,
    }

    def _generate_outer_contour(self) -> VertexLoop:
        """Generate triangular outer contour"""
        return VertexTriangle(
            cx=0, cy=0, size=self.size, num_vertices=self._num_vertices
        )
