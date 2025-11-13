"""VertexLine - line (open or closed) as a VertexLoop"""

from __future__ import annotations
from typing import Tuple

from .vertex_loop import VertexLoop


class VertexLine(VertexLoop):
    """Line (open or closed) as a VertexLoop

    Generates a line with vertices interpolated between start and end points.
    The num_vertices parameter is crucial for morphing - shapes with the same
    num_vertices can morph smoothly between each other.
    """

    def __init__(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        num_vertices: int = 128,
        closed: bool = False
    ):
        """Create a line as a vertex loop

        Args:
            start: Starting point (x, y)
            end: Ending point (x, y)
            num_vertices: Number of vertices to interpolate (important for morphing!)
            closed: Whether to close the line (connects end back to start)
        """
        if num_vertices < 2:
            raise ValueError("Line requires at least 2 vertices")

        vertices = []
        for i in range(num_vertices):
            t = i / (num_vertices - 1) if num_vertices > 1 else 0
            x = start[0] + t * (end[0] - start[0])
            y = start[1] + t * (end[1] - start[1])
            vertices.append((x, y))

        super().__init__(vertices, closed=closed)
