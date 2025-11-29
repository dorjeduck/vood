"""VertexLoop class - sequence of vertices forming an open or closed path"""

from __future__ import annotations
from typing import List, Tuple, Optional
from vood.core.point2d import Points2D,Point2D
import math


class VertexLoop:
    """A sequence of vertices forming an open or closed loop

    Provides utilities for geometric operations like centroid, area, and bounds.
    Can be subclassed for specific geometric primitives.
    """

    def __init__(
        self,
        vertices: Points2D,
        closed: bool = True
    ):
        """Initialize a vertex loop

        Args:
            vertices: List of (x, y) tuples
            closed: Whether the loop is closed (connects last to first)
        """
        if not vertices:
            raise ValueError("VertexLoop requires at least one vertex")

        # Ensure vertices are Point2D objects
        self._vertices = [
            v if isinstance(v, Point2D) else Point2D(v[0], v[1])
            for v in vertices
        ]
        self._closed = closed

    @property
    def vertices(self) -> Points2D:
        """Get vertices as list of tuples"""
        return self._vertices.copy()

    @property
    def closed(self) -> bool:
        """Whether this loop is closed"""
        return self._closed

    def __len__(self) -> int:
        """Number of vertices in the loop"""
        return len(self._vertices)

    def __getitem__(self, index: int) -> Point2D:
        """Get vertex at index"""
        return self._vertices[index]

    def centroid(self) -> Point2D:
        """Calculate the centroid (geometric center) of the vertices

        For closed loops, uses the signed area formula.
        For open loops, uses simple average.
        """
        if not self._vertices:
            return Point2D(0.0, 0.0)

        if not self._closed:
            # Simple average for open loops
            x_sum = sum(v.x for v in self._vertices)
            y_sum = sum(v.y for v in self._vertices)
            n = len(self._vertices)
            return Point2D(x_sum / n, y_sum / n)

        # Signed area formula for closed loops
        area = 0.0
        cx = 0.0
        cy = 0.0

        n = len(self._vertices)
        for i in range(n):
            v1 = self._vertices[i]
            v2 = self._vertices[(i + 1) % n]
            cross = v1.x * v2.y - v2.x * v1.y
            area += cross
            cx += (v1.x + v2.x) * cross
            cy += (v1.y + v2.y) * cross

        if abs(area) < 1e-10:
            # Degenerate case - fall back to simple average
            x_sum = sum(v.x for v in self._vertices)
            y_sum = sum(v.y for v in self._vertices)
            return Point2D(x_sum / n, y_sum / n)

        area *= 0.5
        cx /= (6.0 * area)
        cy /= (6.0 * area)

        return Point2D(cx, cy)

    def area(self) -> float:
        """Calculate the signed area of the loop

        Positive for counter-clockwise winding, negative for clockwise.
        Returns 0 for open loops.
        """
        if not self._closed or len(self._vertices) < 3:
            return 0.0

        area = 0.0
        n = len(self._vertices)

        for i in range(n):
            v1 = self._vertices[i]
            v2 = self._vertices[(i + 1) % n]
            area += v1.x * v2.y - v2.x * v1.y

        return area * 0.5

    def bounds(self) -> Tuple[float, float, float, float]:
        """Calculate bounding box (min_x, min_y, max_x, max_y)"""
        if not self._vertices:
            return (0.0, 0.0, 0.0, 0.0)

        xs = [v.x for v in self._vertices]
        ys = [v.y for v in self._vertices]

        return (min(xs), min(ys), max(xs), max(ys))

    def is_clockwise(self) -> bool:
        """Check if the loop has clockwise winding (negative area)"""
        return self.area() < 0

    def reverse(self) -> VertexLoop:
        """Return a new VertexLoop with reversed vertex order"""
        return VertexLoop(list(reversed(self._vertices)), self._closed)

    def translate(self, dx: float, dy: float) -> VertexLoop:
        """Translate vertices in-place by (dx, dy)

        Returns self for method chaining.
        """
        for v in self._vertices:
            v.x += dx
            v.y += dy
        return self

    def scale(self, sx: float, sy: Optional[float] = None) -> VertexLoop:
        """Scale vertices in-place by (sx, sy)

        If sy is None, uses sx for both dimensions (uniform scaling).
        Returns self for method chaining.
        """
        if sy is None:
            sy = sx

        for v in self._vertices:
            v.x *= sx
            v.y *= sy
        return self

    def rotate(self, angle_degrees: float, center: Optional[Point2D] = None) -> VertexLoop:
        """Rotate vertices in-place by angle_degrees around center

        Args:
            angle_degrees: Rotation angle in degrees (positive = counter-clockwise)
            center: Center of rotation (default is origin)

        Returns self for method chaining.
        """
        if center is None:
            center = Point2D(0.0, 0.0)

        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        for v in self._vertices:
            # Translate to origin
            x_rel = v.x - center.x
            y_rel = v.y - center.y

            # Rotate
            x_new = x_rel * cos_a - y_rel * sin_a
            y_new = x_rel * sin_a + y_rel * cos_a

            # Translate back
            v.x = x_new + center.x
            v.y = y_new + center.y

        return self
