"""VertexStar - star shape as a VertexLoop"""

from __future__ import annotations
import math

from .vertex_loop import VertexLoop


class VertexStar(VertexLoop):
    """Star shape as a VertexLoop

    Generates a star with alternating outer and inner radius points.
    The num_vertices parameter controls morphing quality - shapes with the same
    num_vertices can morph smoothly between each other.
    """

    def __init__(
        self,
        cx: float = 0.0,
        cy: float = 0.0,
        outer_radius: float = 50.0,
        inner_radius: float = 20.0,
        num_points: int = 5,
        num_vertices: int = 128,
    ):
        """Create a star as a vertex loop

        Args:
            cx: Center x coordinate
            cy: Center y coordinate
            outer_radius: Distance from center to outer points (tips)
            inner_radius: Distance from center to inner points (valleys)
            num_points: Number of star points (minimum 3)
            num_vertices: Total vertices distributed along perimeter (important for morphing!)
        """
        if num_points < 3:
            raise ValueError("Star requires at least 3 points")
        if num_vertices < 3:
            raise ValueError("Star requires at least 3 vertices")

        # Calculate star corner vertices (alternating outer/inner)
        corners = []
        for i in range(num_points * 2):
            angle = math.radians(i * 180 / num_points)
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = cx + radius * math.sin(angle)
            y = cy - radius * math.cos(angle)
            corners.append((x, y))

        # Calculate edge lengths between corners
        def distance(p1, p2):
            return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

        num_edges = len(corners)
        edge_lengths = [
            distance(corners[i], corners[(i + 1) % num_edges]) for i in range(num_edges)
        ]
        total_perimeter = sum(edge_lengths)

        # Distribute vertices evenly along perimeter
        vertices = []
        for i in range(num_vertices - 1):
            target_distance = (i / (num_vertices - 1)) * total_perimeter

            cumulative = 0
            for edge_idx in range(num_edges):
                if cumulative + edge_lengths[edge_idx] >= target_distance:
                    distance_along_edge = target_distance - cumulative
                    v1 = corners[edge_idx]
                    v2 = corners[(edge_idx + 1) % num_edges]
                    t = distance_along_edge / edge_lengths[edge_idx]

                    x = v1[0] + t * (v2[0] - v1[0])
                    y = v1[1] + t * (v2[1] - v1[1])
                    vertices.append((x, y))
                    break
                cumulative += edge_lengths[edge_idx]

        # Last vertex equals first to close the loop
        vertices.append(vertices[0])

        super().__init__(vertices, closed=True)
