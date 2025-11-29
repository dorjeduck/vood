"""VertexContours class - outer contour with optional holes"""

from __future__ import annotations
from typing import List, Tuple, Optional

from .vertex_loop import VertexLoop
from vood.core.point2d import Points2D,Point2D

class VertexContours:
    """A shape defined by an outer contour and optional holes

    This represents a potentially multi-contour shape:
    - outer: The outer boundary (VertexLoop, must be closed)
    - holes: List of inner boundaries that create holes (all must be closed)

    The outer contour should have counter-clockwise winding (positive area).
    Holes should have clockwise winding (negative area).
    """

    def __init__(
        self,
        outer: VertexLoop,
        holes: Optional[List[VertexLoop]] = None
    ):
        """Initialize vertex contours

        Args:
            outer: Outer boundary loop (must be closed)
            holes: Optional list of hole loops (all must be closed)
        """
        if not outer.closed and (holes is not None and len(holes)>0):
            raise ValueError("Outer contour must be closed")

        if holes:
            for i, hole in enumerate(holes):
                if not hole.closed:
                    raise ValueError(f"Hole {i} must be closed")

        self._outer = outer
        self._holes = list(holes) if holes else []

    @property
    def outer(self) -> VertexLoop:
        """Get the outer contour"""
        return self._outer

    @property
    def holes(self) -> List[VertexLoop]:
        """Get the list of holes"""
        return self._holes.copy()

    @property
    def has_holes(self) -> bool:
        """Check if this shape has any holes"""
        return len(self._holes) > 0

    def num_holes(self) -> int:
        """Get the number of holes"""
        return len(self._holes)

    def all_loops(self) -> List[VertexLoop]:
        """Get all loops (outer + holes) as a list"""
        return [self._outer] + self._holes

    def total_vertices(self) -> int:
        """Get total number of vertices across all contours"""
        return sum(len(loop) for loop in self.all_loops())

    def bounds(self) -> Tuple[float, float, float, float]:
        """Calculate bounding box of the entire shape (min_x, min_y, max_x, max_y)"""
        return self._outer.bounds()

    def centroid(self) -> Point2D:
        """Calculate centroid of the outer contour"""
        return self._outer.centroid()

    def translate(self, dx: float, dy: float) -> VertexContours:
        """Translate all contours in-place by (dx, dy)

        Returns self for method chaining.
        """
        self._outer.translate(dx, dy)
        for hole in self._holes:
            hole.translate(dx, dy)
        return self

    def scale(self, sx: float, sy: Optional[float] = None) -> VertexContours:
        """Scale all contours in-place by (sx, sy)

        If sy is None, uses sx for both dimensions (uniform scaling).
        Returns self for method chaining.
        """
        self._outer.scale(sx, sy)
        for hole in self._holes:
            hole.scale(sx, sy)
        return self

    def rotate(self, angle_degrees: float, center: Optional[Point2D] = None) -> VertexContours:
        """Rotate all contours in-place around center

        Args:
            angle_degrees: Rotation angle in degrees (positive = counter-clockwise)
            center: Center of rotation (default is origin)

        Returns self for method chaining.
        """
        self._outer.rotate(angle_degrees, center)
        for hole in self._holes:
            hole.rotate(angle_degrees, center)
        return self

    @classmethod
    def from_single_loop(cls, vertices: Points2D, closed: bool = True) -> VertexContours:
        """Create VertexContours from a single loop (no holes)

        Convenience method for simple shapes without holes.
        """
        loop = VertexLoop(vertices, closed=closed)
        return cls(loop, holes=None)

    @classmethod
    def from_vertices_lists(
        cls,
        outer_vertices: Points2D,
        holes_vertices: Optional[List[Points2D]] = None
    ) -> VertexContours:
        """Create VertexContours from lists of vertex tuples

        Args:
            outer_vertices: Vertices for outer contour
            holes_vertices: Optional list of vertex lists for holes
        """
        outer_loop = VertexLoop(outer_vertices, closed=True)

        holes_loops = None
        if holes_vertices:
            holes_loops = [VertexLoop(hole_verts, closed=True) for hole_verts in holes_vertices]

        return cls(outer_loop, holes_loops)

    def __repr__(self) -> str:
        return f"VertexContours(outer={len(self._outer)} vertices, holes={len(self._holes)})"
