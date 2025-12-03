"""Perforated circle state - circle with  holes"""

from __future__ import annotations
from dataclasses import dataclass

from .base import PerforatedVertexState
from vood.component.state.base import State
from vood.component.vertex import VertexCircle, VertexLoop
from vood.transition import easing


@dataclass(frozen=True)
class PerforatedCircleState(PerforatedVertexState):
    """Circle with  holes

    A circular outer shape with zero or more vertex loops of arbitrary shapes.

    Args:
        radius: Circle radius
         holes : List of Shape objects specifying hole geometry and positions

    Example:
        PerforatedCircleState(
            radius=100,
             holes =[
                Circle(radius=20, x=-30, y=0),
                Star(outer_radius=15, inner_radius=7, num_points=5, x=30, y=0),
            ],
            fill_color=Color("#4ECDC4"),
        )
    """

    radius: float = 100

    DEFAULT_EASING = {
        **PerforatedVertexState.DEFAULT_EASING,
        "radius": easing.in_out,
    }

    def _generate_outer_contour(self) -> VertexLoop:
        """Generate circular outer contour"""
        return VertexCircle(
            cx=0, cy=0, radius=self.radius, num_vertices=self._num_vertices
        )
