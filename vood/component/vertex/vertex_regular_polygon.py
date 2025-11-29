"""VertexRegularPolygon - regular n-sided polygon as a VertexLoop"""

from __future__ import annotations
import math

from .vertex_loop import VertexLoop

from vood.core.point2d import Point2D

class VertexRegularPolygon(VertexLoop):
    """Regular n-sided polygon as a VertexLoop

    Generates a regular polygon with any number of sides, with vertices
    distributed along its perimeter. The num_vertices parameter is crucial
    for morphing - shapes with the same num_vertices can morph smoothly
    between each other.
    """

    def __init__(
        self,
        cx: float = 0.0,
        cy: float = 0.0,
        size: float = 50.0,
        num_sides: int = 6,
        num_vertices: int = 128,
        rotation: float = 0.0
    ):
        """Create a regular polygon as a vertex loop

        Args:
            cx: Center x coordinate
            cy: Center y coordinate
            size: Distance from center to vertices (circumradius)
            num_sides: Number of polygon sides (3=triangle, 4=square, etc.)
            num_vertices: Number of vertices distributed along perimeter (important for morphing!)
            rotation: Rotation in degrees (0° = North, 90° = East, Vood convention)
        """
        if num_sides < 3:
            raise ValueError(f"Polygon requires at least 3 sides, got {num_sides}")
        if num_vertices < num_sides:
            raise ValueError(f"num_vertices ({num_vertices}) must be at least num_sides ({num_sides})")

        # Calculate corner positions
        corners = []
        for i in range(num_sides):
            # Vood convention: 0° = North, so start at -90° in standard coords
            angle = math.radians(i * (360 / num_sides) - 90 + rotation)
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            corners.append(Point2D(x, y))

        # Calculate perimeter and side lengths
        def distance(p1: Point2D, p2: Point2D) -> float:
            return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)

        side_lengths = [distance(corners[i], corners[(i + 1) % num_sides]) for i in range(num_sides)]
        perimeter = sum(side_lengths)

        # Distribute vertices along perimeter
        vertices = []
        for i in range(num_vertices - 1):
            target_distance = (i / (num_vertices - 1)) * perimeter

            # Find which side we're on
            cumulative = 0
            for side_idx in range(num_sides):
                if cumulative + side_lengths[side_idx] >= target_distance:
                    distance_along_side = target_distance - cumulative
                    start_corner = corners[side_idx]
                    end_corner = corners[(side_idx + 1) % num_sides]
                    t = distance_along_side / side_lengths[side_idx]

                    x = start_corner.x + t * (end_corner.x - start_corner.x)
                    y = start_corner.y + t * (end_corner.y - start_corner.y)
                    vertices.append(Point2D(x, y))
                    break
                cumulative += side_lengths[side_idx]

        # Last vertex equals first to close the loop
        vertices.append(vertices[0])    

        super().__init__(vertices, closed=True)
