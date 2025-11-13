"""VertexSquare - square as a VertexLoop"""

from __future__ import annotations

from .vertex_rectangle import VertexRectangle


class VertexSquare(VertexRectangle):
    """Square as a VertexLoop (special case of VertexRectangle)

    Generates a square with vertices distributed along its perimeter.
    The num_vertices parameter is crucial for morphing - shapes with the same
    num_vertices can morph smoothly between each other.
    """

    def __init__(
        self,
        cx: float = 0.0,
        cy: float = 0.0,
        size: float = 100.0,
        num_vertices: int = 128
    ):
        """Create a square as a vertex loop

        Args:
            cx: Center x coordinate
            cy: Center y coordinate
            size: Side length of the square
            num_vertices: Number of vertices distributed along perimeter (important for morphing!)
        """
        # Square is just a rectangle with equal width and height
        super().__init__(
            cx=cx,
            cy=cy,
            width=size,
            height=size,
            num_vertices=num_vertices
        )
