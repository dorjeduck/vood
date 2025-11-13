"""Perforated star state - star with holes"""

from __future__ import annotations
from dataclasses import dataclass

from .base import PerforatedVertexState
from vood.component.state.base import State
from vood.component.vertex import VertexStar, VertexLoop
from vood.transition import easing


@dataclass(frozen=True)
class PerforatedStarState(PerforatedVertexState):
    """Star with holes

    A star-shaped outer contour with zero or more holes of arbitrary shapes.

    Args:
        outer_radius: Distance from center to outer points (tips)
        inner_radius: Distance from center to inner points (valleys)
        num_points: Number of star points (minimum 3)
        holes: List of Shape objects specifying hole geometry and positions

    Example:
        PerforatedStarState(
            outer_radius=100,
            inner_radius=50,
            num_points=5,
            holes=[Circle(radius=20, x=0, y=0)],
            fill_color=Color("#FFD700"),
        )
    """

    outer_radius: float = 100
    inner_radius: float = 50
    num_points: int = 5

    DEFAULT_EASING = {
        **PerforatedVertexState.DEFAULT_EASING,
        "outer_radius": easing.in_out,
        "inner_radius": easing.in_out,
        "num_points": easing.step,  # Integer, step interpolation
    }

    def _generate_outer_contour(self) -> VertexLoop:
        """Generate star outer contour"""
        return VertexStar(
            cx=0, cy=0,
            outer_radius=self.outer_radius,
            inner_radius=self.inner_radius,
            num_points=self.num_points,
            num_vertices=self._num_vertices
        )
