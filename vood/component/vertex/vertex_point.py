"""Degenerate vertex loop representing a single point

Used for shape disappearance/appearance transitions.
"""

from vood.core.point2d import Point2D
from .vertex_loop import VertexLoop


class VertexPoint(VertexLoop):
    """A degenerate vertex loop with all vertices at the same point

    Used to represent the collapsed state of a shape for morphing purposes.
    During interpolation, shapes can morph to/from a VertexPoint, creating
    smooth appearance/disappearance effects.

    Args:
        cx: X coordinate of the point
        cy: Y coordinate of the point
        num_vertices: Number of vertices (all at same location, default 4)
    """

    def __init__(self, cx: float = 0.0, cy: float = 0.0, num_vertices: int = 4):
        # Create all vertices at the same point
        vertices = [Point2D(cx, cy) for _ in range(num_vertices)]
        super().__init__(vertices, closed=True)
