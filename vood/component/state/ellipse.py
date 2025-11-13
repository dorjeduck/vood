"""Ellipse state implementation using VertexContours"""

from __future__ import annotations
from dataclasses import dataclass

from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexEllipse

from .base import State

from vood.transition import easing
from vood.core.color import Color


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

    @staticmethod
    def get_renderer_class():
        """Get the primitive renderer for static/keystate rendering"""
        from ..renderer.ellipse import EllipseRenderer

        return EllipseRenderer

    @staticmethod
    def get_vertex_renderer_class():
        """Get the vertex renderer for morphing transitions"""
        from ..renderer.base_vertex import VertexRenderer

        return VertexRenderer

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
