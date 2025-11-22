"""Rectangle state implementation using VertexContours"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexRectangle

from vood.transition import easing
from vood.core.color import Color


@dataclass(frozen=True)
class RectangleState(VertexState):
    """State class for rectangle elements"""

    width: float = 100
    height: float = 60
    fill_color: Optional[Color] = Color(0, 0, 255)
    fill_opacity: float = 1
    stroke_color: Optional[Color] = Color.NONE
    stroke_opacity: float = 1
    corner_radius: float = 0  # For rounded rectangles (TODO: implement)

    # Default easing functions for each property
    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "width": easing.in_out,
        "height": easing.in_out,
        "fill_color": easing.linear,
        "stroke_color": easing.linear,
        "fill_opacity": easing.linear,
        "stroke_opacity": easing.linear,
        "stroke_width": easing.in_out,
        "corner_radius": easing.in_out,
        "rotation": easing.in_out,
    }

    def __post_init__(self):
        super().__post_init__()
        self._none_color("fill_color")
        self._none_color("stroke_color")



    def _generate_contours(self) -> VertexContours:
        """Generate rectangle contours

        Returns VertexContours with a single rectangular outer contour, no holes.
        """
        rectangle = VertexRectangle(
            cx=0,
            cy=0,
            width=self.width,
            height=self.height,
            num_vertices=self._num_vertices,
        )

        return VertexContours(outer=rectangle, holes=None)
