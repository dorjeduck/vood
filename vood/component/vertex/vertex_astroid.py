"""VertexAstroid - astroid shape with inward-curving cusps as a VertexLoop"""

from __future__ import annotations
import math

from .vertex_loop import VertexLoop


class VertexAstroid(VertexLoop):
    """Astroid as a VertexLoop - star-like shape with inward-curving cusps

    Generates an astroid shape with cusps (pointed tips) connected by
    inward-bending circular arcs. The classic astroid has 4 cusps, but
    this implementation supports any number.

    The num_vertices parameter is crucial for morphing - shapes with the same
    num_vertices can morph smoothly between each other.
    """

    def __init__(
        self,
        cx: float = 0.0,
        cy: float = 0.0,
        radius: float = 50.0,
        num_cusps: int = 4,
        curvature: float = 0.7,
        num_vertices: int = 128
    ):
        """Create an astroid as a vertex loop

        Args:
            cx: Center x coordinate
            cy: Center y coordinate
            radius: Distance from center to cusp points
            num_cusps: Number of cusps (points) - 4 for classic astroid
            curvature: Controls arc depth (0-1). Higher = deeper inward curves
            num_vertices: Number of vertices distributed along perimeter (important for morphing!)
        """
        if num_cusps < 3:
            raise ValueError(f"Astroid requires at least 3 cusps, got {num_cusps}")
        if num_vertices < num_cusps:
            raise ValueError(f"num_vertices ({num_vertices}) must be at least num_cusps ({num_cusps})")
        if not 0 <= curvature <= 1:
            raise ValueError(f"curvature must be between 0 and 1, got {curvature}")

        # Calculate cusp positions (the pointed tips)
        cusps = []
        for i in range(num_cusps):
            angle = math.radians(i * (360 / num_cusps) - 90)  # -90 to start at top
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            cusps.append((x, y))

        # Generate vertices along the astroid curve
        vertices = self._generate_astroid_vertices(
            cusps, curvature, num_vertices, cx, cy
        )

        super().__init__(vertices, closed=True)

    def _generate_astroid_vertices(
        self,
        cusps: list[tuple[float, float]],
        curvature: float,
        num_vertices: int,
        cx: float,
        cy: float
    ) -> list[tuple[float, float]]:
        """Generate vertices along the astroid curve

        The astroid is formed by connecting cusp points with inward-bending
        circular arcs. We sample points along these arcs.

        Args:
            cusps: List of cusp point coordinates
            curvature: How much the arcs curve inward (0-1)
            num_vertices: Total number of vertices to generate
            cx: Center x coordinate
            cy: Center y coordinate

        Returns:
            List of (x, y) vertex coordinates
        """
        num_cusps = len(cusps)
        vertices = []

        # Calculate how many vertices per arc segment
        vertices_per_segment = num_vertices // num_cusps

        for i in range(num_cusps):
            start_cusp = cusps[i]
            end_cusp = cusps[(i + 1) % num_cusps]

            # Generate vertices along the arc between these cusps
            for j in range(vertices_per_segment):
                t = j / vertices_per_segment  # 0 to 1 along this arc

                # Calculate point along inward-bending arc
                # Use a simple quadratic Bezier curve with control point pulled inward

                # Control point: midpoint pulled toward center
                mid_x = (start_cusp[0] + end_cusp[0]) / 2
                mid_y = (start_cusp[1] + end_cusp[1]) / 2

                # Pull control point toward center based on curvature
                control_x = mid_x + (cx - mid_x) * curvature
                control_y = mid_y + (cy - mid_y) * curvature

                # Quadratic Bezier curve
                # B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
                one_minus_t = 1 - t

                x = (one_minus_t ** 2 * start_cusp[0] +
                     2 * one_minus_t * t * control_x +
                     t ** 2 * end_cusp[0])

                y = (one_minus_t ** 2 * start_cusp[1] +
                     2 * one_minus_t * t * control_y +
                     t ** 2 * end_cusp[1])

                vertices.append((x, y))

        # Ensure we have exactly num_vertices by adding any remaining
        while len(vertices) < num_vertices:
            vertices.append(vertices[0])  # Duplicate first vertex to close

        return vertices[:num_vertices]
