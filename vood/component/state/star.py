"""Star renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple

from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexStar

from .base import State
from vood.transition import easing
from vood.core.color import Color


@dataclass(frozen=True)
class StarState(VertexState):
    """State class for star elements"""

    outer_radius: float = 50  # Radius to outer points
    inner_radius: float = 20  # Radius to inner points
    num_points_star: int = 5  # Number of points (minimum 3)

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "outer_radius": easing.in_out,
        "inner_radius": easing.in_out,
        "num_points_star": easing.linear,  # Stepped animation for integers
    }

    def __post_init__(self):
        self._none_color("fill_color")
        self._none_color("stroke_color")

    @staticmethod
    def get_renderer_class():
        from ..renderer.star import StarRenderer

        return StarRenderer

    def _generate_contours(self) -> VertexContours:
        """Generate star vertices"""
        star = VertexStar(
            cx=0,
            cy=0,
            outer_radius=self.outer_radius,
            inner_radius=self.inner_radius,
            num_points=self.num_points_star,
            num_vertices=self._num_vertices,
        )
        return VertexContours(outer=star, holes=None)
