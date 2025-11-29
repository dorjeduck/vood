"""VertexRectangle - rectangle as a VertexLoop"""

from __future__ import annotations

from .vertex_loop import VertexLoop

from vood.core.point2d import Point2D

class VertexRectangle(VertexLoop):
    """Rectangle as a VertexLoop

    Generates a rectangle with vertices distributed along its perimeter.
    The num_vertices parameter is crucial for morphing - shapes with the same
    num_vertices can morph smoothly between each other.
    """

    def __init__(
        self,
        cx: float = 0.0,
        cy: float = 0.0,
        width: float = 100.0,
        height: float = 100.0,
        num_vertices: int = 128
    ):
        """Create a rectangle as a vertex loop

        Args:
            cx: Center x coordinate
            cy: Center y coordinate
            width: Rectangle width
            height: Rectangle height
            num_vertices: Number of vertices distributed along perimeter (important for morphing!)
        """
        if num_vertices < 4:
            raise ValueError("Rectangle requires at least 4 vertices")

        # Calculate half dimensions
        hw = width / 2
        hh = height / 2

        # Rectangle corners (top-left, top-right, bottom-right, bottom-left)
        corners = [
            Point2D(cx - hw, cy - hh),  # Top-left
            Point2D(cx + hw, cy - hh),  # Top-right
            Point2D(cx + hw, cy + hh),  # Bottom-right
            Point2D(cx - hw, cy + hh),  # Bottom-left
        ]

        # Perimeter lengths for each side
        perimeter = 2 * (width + height)
        side_lengths = [width, height, width, height]

        # Distribute vertices along perimeter
        # Use the same approach as other shapes: iterate through all vertices
        # and calculate position based on distance along perimeter
        vertices = []

        for i in range(num_vertices - 1):
            # Calculate target distance along perimeter
            target_distance = (i / (num_vertices - 1)) * perimeter

            # Find which side we're on
            cumulative = 0
            for side_idx in range(4):
                if cumulative + side_lengths[side_idx] >= target_distance:
                    # We're on this side
                    distance_along_side = target_distance - cumulative
                    start_corner = corners[side_idx]
                    end_corner = corners[(side_idx + 1) % 4]
                    t = distance_along_side / side_lengths[side_idx]

                    x = start_corner.x + t * (end_corner.x - start_corner.x)
                    y = start_corner.y + t * (end_corner.y - start_corner.y)
                    vertices.append(Point2D(x, y))
                    break
                cumulative += side_lengths[side_idx]

        # Last vertex equals first to close the loop
        vertices.append(vertices[0])

        super().__init__(vertices, closed=True)
