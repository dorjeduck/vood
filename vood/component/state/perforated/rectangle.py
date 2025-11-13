"""Perforated rectangle state - rectangle with holes"""

from __future__ import annotations
from dataclasses import dataclass

from .base import PerforatedVertexState
from vood.component.state.base import State
from vood.component.vertex import VertexRectangle, VertexLoop
from vood.transition import easing


@dataclass(frozen=True)
class PerforatedRectangleState(PerforatedVertexState):
    """Rectangle with holes

    A rectangular outer shape with zero or more holes of arbitrary shapes.

    Args:
        width: Rectangle width
        height: Rectangle height
        holes: List of Shape objects specifying hole geometry and positions

    Example:
        PerforatedRectangleState(
            width=200,
            height=150,
            holes=[
                Circle(radius=20, x=-50, y=0),
                Circle(radius=20, x=50, y=0),
            ],
            fill_color=Color("#E74C3C"),
        )
    """

    width: float = 160
    height: float = 100

    DEFAULT_EASING = {
        **PerforatedVertexState.DEFAULT_EASING,
        "width": easing.in_out,
        "height": easing.in_out,
    }

    def _generate_outer_contour(self) -> VertexLoop:
        """Generate rectangular outer contour"""
        return VertexRectangle(
            cx=0, cy=0,
            width=self.width,
            height=self.height,
            num_vertices=self._num_vertices
        )
