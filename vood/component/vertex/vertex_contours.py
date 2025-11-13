"""VertexContours class - outer contour with optional holes"""

from __future__ import annotations
from typing import List, Tuple, Optional

from .vertex_loop import VertexLoop


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

    def centroid(self) -> Tuple[float, float]:
        """Calculate centroid of the outer contour"""
        return self._outer.centroid()

    def translate(self, dx: float, dy: float) -> VertexContours:
        """Return new VertexContours translated by (dx, dy)"""
        translated_outer = self._outer.translate(dx, dy)
        translated_holes = [hole.translate(dx, dy) for hole in self._holes]
        return VertexContours(translated_outer, translated_holes)

    def scale(self, sx: float, sy: Optional[float] = None) -> VertexContours:
        """Return new VertexContours scaled by (sx, sy)"""
        scaled_outer = self._outer.scale(sx, sy)
        scaled_holes = [hole.scale(sx, sy) for hole in self._holes]
        return VertexContours(scaled_outer, scaled_holes)

    def rotate(self, angle_degrees: float, center: Optional[Tuple[float, float]] = None) -> VertexContours:
        """Return new VertexContours rotated around center"""
        rotated_outer = self._outer.rotate(angle_degrees, center)
        rotated_holes = [hole.rotate(angle_degrees, center) for hole in self._holes]
        return VertexContours(rotated_outer, rotated_holes)

    @classmethod
    def from_single_loop(cls, vertices: List[Tuple[float, float]], closed: bool = True) -> VertexContours:
        """Create VertexContours from a single loop (no holes)

        Convenience method for simple shapes without holes.
        """
        loop = VertexLoop(vertices, closed=closed)
        return cls(loop, holes=None)

    @classmethod
    def from_vertices_lists(
        cls,
        outer_vertices: List[Tuple[float, float]],
        holes_vertices: Optional[List[List[Tuple[float, float]]]] = None
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
