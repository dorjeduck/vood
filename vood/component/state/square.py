"""Rectangle renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

from .base_vertex import VertexState
from vood.component.vertex import VertexContours

from vood.transition import easing


@dataclass(frozen=True)
class SquareState(VertexState):
    """State class for rectangle elements"""

    size: float = 100
    # Default easing functions for each property
    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "size": easing.in_out,
        "rotation": easing.in_out,
    }


    def _generate_contours(self) -> VertexContours:
        """Generate square vertices, starting at top-left, going clockwise"""
        half = self.size / 2
        perimeter = 4 * self.size

        vertices = []
        for i in range(self._num_vertices - 1):
            distance = (i / (self._num_vertices - 1)) * perimeter

            if distance < self.size:  # Top edge
                x = -half + distance
                y = -half
            elif distance < 2 * self.size:  # Right edge
                x = half
                y = -half + (distance - self.size)
            elif distance < 3 * self.size:  # Bottom edge
                x = half - (distance - 2 * self.size)
                y = half
            else:  # Left edge
                x = -half
                y = half - (distance - 3 * self.size)

            vertices.append((x, y))

        vertices.append(vertices[0])
        return VertexContours.from_single_loop(vertices, closed=True)
