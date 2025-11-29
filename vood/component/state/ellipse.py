"""Ellipse state implementation using VertexContours"""

from __future__ import annotations
from dataclasses import dataclass

from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexEllipse
from vood.component.registry import renderer
from vood.component.renderer.ellipse import EllipseRenderer

from .base import State

from vood.transition import easing
from vood.core.color import Color


@renderer(EllipseRenderer)
@dataclass(frozen=True)
class EllipseState(VertexState):
    """State class for ellipse elements"""

    rx: float = 60  # Horizontal radius
    ry: float = 40  # Vertical radius

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "rx": easing.in_out,
        "ry": easing.in_out,
    }

    def __post_init__(self):
        super().__post_init__()
        self._none_color("fill_color")
        self._none_color("stroke_color")



    def _generate_contours(self) -> VertexContours:
        """Generate ellipse contours

        Returns VertexContours with a single elliptical outer contour, no holes.
        """
        ellipse = VertexEllipse(
            cx=0,
            cy=0,
            rx=self.rx,
            ry=self.ry,
            num_vertices=self._num_vertices,
            start_angle=0.0,
        )

        return VertexContours(outer=ellipse, holes=None)
