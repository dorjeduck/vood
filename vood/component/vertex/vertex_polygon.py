"""VertexPolygon - arbitrary polygon as a VertexLoop"""

from __future__ import annotations
from typing import List, Tuple

from .vertex_loop import VertexLoop


class VertexPolygon(VertexLoop):
    """Arbitrary polygon as a VertexLoop

    Creates a polygon from arbitrary vertices. Optionally redistributes vertices
    to achieve a specific num_vertices count for morphing compatibility.
    """

    def __init__(
        self,
        vertices: List[Tuple[float, float]],
        closed: bool = True,
        auto_close: bool = True,
        num_vertices: int = None
    ):
        """Create a polygon from arbitrary vertices

        Args:
            vertices: List of (x, y) tuples defining the polygon
            closed: Whether the polygon is closed
            auto_close: If True and closed=True, ensures last vertex equals first
            num_vertices: If provided, redistributes vertices to this count (important for morphing!)
        """
        if not vertices:
            raise ValueError("Polygon requires at least one vertex")

        verts = list(vertices)

        # Auto-close if requested
        if closed and auto_close and len(verts) > 1:
            # Check if already closed
            first = verts[0]
            last = verts[-1]
            distance = ((last[0] - first[0]) ** 2 + (last[1] - first[1]) ** 2) ** 0.5

            if distance > 1e-6:  # Not already closed
                verts.append(first)

        # If num_vertices specified, redistribute vertices along perimeter
        if num_vertices is not None and num_vertices != len(verts):
            verts = self._redistribute_vertices(verts, num_vertices, closed)

        super().__init__(verts, closed=closed)

    @staticmethod
    def _redistribute_vertices(
        vertices: List[Tuple[float, float]],
        num_vertices: int,
        closed: bool
    ) -> List[Tuple[float, float]]:
        """Redistribute vertices evenly along the polygon perimeter

        Args:
            vertices: Original vertices
            num_vertices: Target number of vertices
            closed: Whether the polygon is closed

        Returns:
            New list of redistributed vertices
        """
        if num_vertices < 2:
            raise ValueError("num_vertices must be at least 2")

        # Calculate cumulative distances along perimeter
        distances = [0.0]
        total_distance = 0.0

        for i in range(len(vertices) - 1):
            x1, y1 = vertices[i]
            x2, y2 = vertices[i + 1]
            dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            total_distance += dist
            distances.append(total_distance)

        if total_distance < 1e-6:
            # Degenerate case - all vertices at same point
            return [vertices[0]] * num_vertices

        # Generate new vertices at evenly spaced distances
        new_vertices = []
        for i in range(num_vertices - 1 if closed else num_vertices):
            target_dist = (i / (num_vertices - 1 if closed else num_vertices - 1)) * total_distance

            # Find which segment this distance falls in
            for j in range(len(distances) - 1):
                if distances[j] <= target_dist <= distances[j + 1]:
                    # Interpolate within this segment
                    segment_start_dist = distances[j]
                    segment_end_dist = distances[j + 1]
                    segment_length = segment_end_dist - segment_start_dist

                    if segment_length > 1e-6:
                        t = (target_dist - segment_start_dist) / segment_length
                    else:
                        t = 0.0

                    x1, y1 = vertices[j]
                    x2, y2 = vertices[j + 1]

                    x = x1 + t * (x2 - x1)
                    y = y1 + t * (y2 - y1)
                    new_vertices.append((x, y))
                    break

        # Close the loop if needed
        if closed and new_vertices:
            new_vertices.append(new_vertices[0])

        return new_vertices
