"""Perforated Square state - Square with holes"""

from __future__ import annotations
from dataclasses import dataclass

from .base import PerforatedVertexState
from vood.component.state.base import State
from vood.component.vertex import VertexSquare, VertexLoop
from vood.transition import easing


@dataclass(frozen=True)
class PerforatedSquareState(PerforatedVertexState):
    """Square with holes

    A square outer shape with zero or more holes of arbitrary shapes.

    Args:
        size: Square size
        holes: List of Shape objects specifying hole geometry and positions

    Example:
        PerforatedSquareState(
            width=200,
            height=150,
            holes=[
                Circle(radius=20, x=-50, y=0),
                Circle(radius=20, x=50, y=0),
            ],
            fill_color=Color("#E74C3C"),
        )
    """

    size: float = 160

    DEFAULT_EASING = {
        **PerforatedVertexState.DEFAULT_EASING,
        "size": easing.in_out,
    }

    def _generate_outer_contour(self) -> VertexLoop:
        """Generate rectangular outer contour"""
        return VertexSquare(cx=0, cy=0, size=self.size, num_vertices=self._num_vertices)
