"""VertexLine - line (open or closed) as a VertexLoop"""

from __future__ import annotations
from typing import Tuple

from .vertex_loop import VertexLoop
from vood.core.point2d import Point2D

class VertexLine(VertexLoop):
    """Line (open or closed) as a VertexLoop

    Generates a line with vertices interpolated between start and end points.
    The num_vertices parameter is crucial for morphing - shapes with the same
    num_vertices can morph smoothly between each other.
    """

    def __init__(
        self,
        start: Point2D,
        end: Point2D,
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
            x = start.x + t * (end.x - start.x)
            y = start.y + t * (end.y - start.y)
            vertices.append(Point2D(x, y))

        super().__init__(vertices, closed=closed)
