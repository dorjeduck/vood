"""VertexCircle - circle approximation as a VertexLoop"""

from __future__ import annotations
import math

from .vertex_loop import VertexLoop


class VertexCircle(VertexLoop):
    """Circle approximation as a VertexLoop

    Generates a circle with a specified number of vertices.
    The num_vertices parameter is crucial for morphing - shapes with the same
    num_vertices can morph smoothly between each other.
    """

    def __init__(
        self,
        cx: float = 0.0,
        cy: float = 0.0,
        radius: float = 50.0,
        num_vertices: int = 128,
        start_angle: float = 0.0
    ):
        """Create a circle as a vertex loop

        Args:
            cx: Center x coordinate
            cy: Center y coordinate
            radius: Circle radius
            num_vertices: Number of vertices to generate (important for morphing!)
            start_angle: Starting angle in degrees (0 = top/north, clockwise)
        """
        if num_vertices < 3:
            raise ValueError("Circle requires at least 3 vertices")

        vertices = []
        start_rad = math.radians(start_angle)

        # Generate num_vertices - 1 distinct positions
        for i in range(num_vertices - 1):
            angle = start_rad + 2 * math.pi * i / (num_vertices - 1)
            x = cx + radius * math.sin(angle)
            y = cy - radius * math.cos(angle)
            vertices.append((x, y))

        # Last vertex equals first to close the loop
        vertices.append(vertices[0])

        super().__init__(vertices, closed=True)
