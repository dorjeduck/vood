"""Line state implementation using VertexContours"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, List, Tuple

from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours
from vood.component.registry import renderer
from vood.component.renderer.line import LineRenderer

from .base import State

from vood.transition import easing


@renderer(LineRenderer)
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
    def from_endpoints(
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stroke_color: Optional[str] = None,
        stroke_width: Optional[float] = None,
        stroke_dasharray: Optional[str] = None,
        stroke_linecap: Optional[str] = None,
        scale: Optional[float] = None,
        rotation: Optional[float] = None,
        opacity: Optional[float] = None,
    ) -> LineState:

        cx, cy, add_rotation, length = line_endpoints_to_center_rotation_length(
            x1, y1, x2, y2
        )
        return LineState(
            cx=cx,
            cy=cy,
            rotation=rotation + add_rotation,
            length=length,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            stroke_dasharray=stroke_dasharray,
            stroke_linecap=stroke_linecap,
            scale=scale,
            opacity=opacity,
        )

    def _generate_contours(self) -> VertexContours:
        """Generate line contours from -length/2 to +length/2 along x-axis"""
        half_length = self.length / 2

        vertices = [
            (-half_length + (i / (self._num_vertices - 1)) * self.length, 0)
            for i in range(self._num_vertices)
        ]

        return VertexContours.from_single_loop(vertices, closed=self.closed)


def line_endpoints_to_center_rotation_length(
    x1: float, y1: float, x2: float, y2: float
) -> Tuple[float, float, float, float]:
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    rotation = math.atan2(y2 - y1, x2 - x1)
    length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return center_x, center_y, rotation, length


def line_center_rotation_length_to_endpoints(
    cx: float, cy: float, rotation: float, length: float
) -> Tuple[float, float, float, float]:
    # Calculate the endpoints based on the center, rotation, and length
    # take rotation into account

    theta = math.radians(90 - rotation)
    h = length / 2
    dx = math.cos(theta)
    dy = math.sin(theta)

    x1 = cx - h * dx
    y1 = cy - h * dy
    x2 = cx + h * dx
    y2 = cy + h * dy

    return x1, y1, x2, y2
