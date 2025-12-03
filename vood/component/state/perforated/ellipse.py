"""Perforated ellipse state - ellipse with  holes"""

from __future__ import annotations
from dataclasses import dataclass

from .base import PerforatedVertexState
from vood.component.vertex import VertexEllipse, VertexLoop
from vood.transition import easing


@dataclass(frozen=True)
class PerforatedEllipseState(PerforatedVertexState):
    """Ellipse with  holes

    An elliptical outer shape with zero or more vertex loops of arbitrary shapes.

    Args:
        rx: Horizontal radius (semi-major axis)
        ry: Vertical radius (semi-minor axis)
         holes : List of Shape objects specifying hole geometry and positions

    Example:
        PerforatedEllipseState(
            rx=120,
            ry=80,
            holes=[Circle(radius=20, x=-40, y=0), Circle(radius=20, x=40, y=0)],
            fill_color=Color("#9B59B6"),
        )
    """

    rx: float = 100
    ry: float = 60

    DEFAULT_EASING = {
        **PerforatedVertexState.DEFAULT_EASING,
        "rx": easing.in_out,
        "ry": easing.in_out,
    }

    def _generate_outer_contour(self) -> VertexLoop:
        """Generate elliptical outer contour"""
        return VertexEllipse(
            cx=0, cy=0, rx=self.rx, ry=self.ry, num_vertices=self._num_vertices
        )
