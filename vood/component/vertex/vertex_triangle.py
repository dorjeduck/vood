"""VertexTriangle - triangle as a VertexLoop"""

from __future__ import annotations
import math

from .vertex_loop import VertexLoop

from vood.core.point2d import Point2D


class VertexTriangle(VertexLoop):
    """Equilateral triangle as a VertexLoop

    Generates an equilateral triangle with vertices distributed along its perimeter.
    The num_vertices parameter is crucial for morphing - shapes with the same
    num_vertices can morph smoothly between each other.
    """

    def __init__(
        self,
        cx: float = 0.0,
        cy: float = 0.0,
        size: float = 50.0,
        num_vertices: int = 128
    ):
        """Create an equilateral triangle as a vertex loop

        Args:
            cx: Center x coordinate
            cy: Center y coordinate
            size: Distance from center to vertices
            num_vertices: Number of vertices distributed along perimeter (important for morphing!)
        """
        if num_vertices < 3:
            raise ValueError("Triangle requires at least 3 vertices")

        # Calculate the three corners of an equilateral triangle
        # Positioned with one vertex pointing up
        corners = []
        for i in range(3):
            angle = math.radians(i * 120 - 90)  # -90 to point first vertex upward
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            corners.append(Point2D(x, y))

        # Calculate side lengths (all equal for equilateral triangle)
        side_length = corners[0].distance_to(corners[1])
        perimeter = 3 * side_length
        side_lengths = [side_length, side_length, side_length]

        # Distribute vertices along perimeter
        vertices = []

        for i in range(num_vertices - 1):
            # Calculate target distance along perimeter
            target_distance = (i / (num_vertices - 1)) * perimeter

            # Find which side we're on
            cumulative = 0
            for side_idx in range(3):
                if cumulative + side_lengths[side_idx] >= target_distance:
                    # We're on this side
                    distance_along_side = target_distance - cumulative
                    start_corner = corners[side_idx]
                    end_corner = corners[(side_idx + 1) % 3]
                    t = distance_along_side / side_lengths[side_idx]

                    x = start_corner.x + t * (end_corner.x - start_corner.x)
                    y = start_corner.y + t * (end_corner.y - start_corner.y)
                    vertices.append(Point2D(x, y))
                    break
                cumulative += side_lengths[side_idx]

        # Last vertex equals first to close the loop
        vertices.append(vertices[0])

        super().__init__(vertices, closed=True)
