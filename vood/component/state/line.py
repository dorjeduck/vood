"""Line state implementation using VertexContours"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple

from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours

from .base import State

from vood.transition import easing


@dataclass(frozen=True)
class LineState(VertexState):
    """State class for line elements"""

    length: float = 100  # Length of the line
    stroke_dasharray: Optional[str] = None  # For dashed lines, e.g., "5,5"
    stroke_linecap: str = "round"  # "butt", "round", "square"
    closed: bool = False

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "length": easing.in_out,
        "stroke_dasharray": easing.linear,  # Stepped animation for strings
        "stroke_linecap": easing.linear,  # Stepped animation for strings
    }

    def __post_init__(self):
        super().__post_init__()
        self._none_color("stroke_color")

    @staticmethod
    def get_renderer_class():
        from ..renderer.line import LineRenderer

        return LineRenderer

    def _generate_contours(self) -> VertexContours:
        """Generate line contours from -length/2 to +length/2 along x-axis"""
        half_length = self.length / 2

        vertices = [
            (-half_length + (i / (self._num_vertices - 1)) * self.length, 0)
            for i in range(self._num_vertices)
        ]

        return VertexContours.from_single_loop(vertices, closed=self.closed)
