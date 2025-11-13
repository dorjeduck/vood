"""VertexLoop class - sequence of vertices forming an open or closed path"""

from __future__ import annotations
from typing import List, Tuple, Optional
import math


class VertexLoop:
    """A sequence of vertices forming an open or closed loop

    Provides utilities for geometric operations like centroid, area, and bounds.
    Can be subclassed for specific geometric primitives.
    """

    def __init__(
        self,
        vertices: List[Tuple[float, float]],
        closed: bool = True
    ):
        """Initialize a vertex loop

        Args:
            vertices: List of (x, y) tuples
            closed: Whether the loop is closed (connects last to first)
        """
        if not vertices:
            raise ValueError("VertexLoop requires at least one vertex")

        self._vertices = list(vertices)  # Make a copy
        self._closed = closed

    @property
    def vertices(self) -> List[Tuple[float, float]]:
        """Get vertices as list of tuples"""
        return self._vertices.copy()

    @property
    def closed(self) -> bool:
        """Whether this loop is closed"""
        return self._closed

    def __len__(self) -> int:
        """Number of vertices in the loop"""
        return len(self._vertices)

    def __getitem__(self, index: int) -> Tuple[float, float]:
        """Get vertex at index"""
        return self._vertices[index]

    def centroid(self) -> Tuple[float, float]:
        """Calculate the centroid (geometric center) of the vertices

        For closed loops, uses the signed area formula.
        For open loops, uses simple average.
        """
        if not self._vertices:
            return (0.0, 0.0)

        if not self._closed:
            # Simple average for open loops
            x_sum = sum(v[0] for v in self._vertices)
            y_sum = sum(v[1] for v in self._vertices)
            n = len(self._vertices)
            return (x_sum / n, y_sum / n)

        # Signed area formula for closed loops
        area = 0.0
        cx = 0.0
        cy = 0.0

        n = len(self._vertices)
        for i in range(n):
            x1, y1 = self._vertices[i]
            x2, y2 = self._vertices[(i + 1) % n]
            cross = x1 * y2 - x2 * y1
            area += cross
            cx += (x1 + x2) * cross
            cy += (y1 + y2) * cross

        if abs(area) < 1e-10:
            # Degenerate case - fall back to simple average
            x_sum = sum(v[0] for v in self._vertices)
            y_sum = sum(v[1] for v in self._vertices)
            return (x_sum / n, y_sum / n)

        area *= 0.5
        cx /= (6.0 * area)
        cy /= (6.0 * area)

        return (cx, cy)

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
            x1, y1 = self._vertices[i]
            x2, y2 = self._vertices[(i + 1) % n]
            area += x1 * y2 - x2 * y1

        return area * 0.5

    def bounds(self) -> Tuple[float, float, float, float]:
        """Calculate bounding box (min_x, min_y, max_x, max_y)"""
        if not self._vertices:
            return (0.0, 0.0, 0.0, 0.0)

        xs = [v[0] for v in self._vertices]
        ys = [v[1] for v in self._vertices]

        return (min(xs), min(ys), max(xs), max(ys))

    def is_clockwise(self) -> bool:
        """Check if the loop has clockwise winding (negative area)"""
        return self.area() < 0

    def reverse(self) -> VertexLoop:
        """Return a new VertexLoop with reversed vertex order"""
        return VertexLoop(list(reversed(self._vertices)), self._closed)

    def translate(self, dx: float, dy: float) -> VertexLoop:
        """Return a new VertexLoop translated by (dx, dy)"""
        translated = [(x + dx, y + dy) for x, y in self._vertices]
        return VertexLoop(translated, self._closed)

    def scale(self, sx: float, sy: Optional[float] = None) -> VertexLoop:
        """Return a new VertexLoop scaled by (sx, sy)

        If sy is None, uses sx for both dimensions (uniform scaling).
        """
        if sy is None:
            sy = sx

        scaled = [(x * sx, y * sy) for x, y in self._vertices]
        return VertexLoop(scaled, self._closed)

    def rotate(self, angle_degrees: float, center: Optional[Tuple[float, float]] = None) -> VertexLoop:
        """Return a new VertexLoop rotated by angle_degrees around center

        Args:
            angle_degrees: Rotation angle in degrees (positive = counter-clockwise)
            center: Center of rotation (default is origin)
        """
        if center is None:
            center = (0.0, 0.0)

        cx, cy = center
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        rotated = []
        for x, y in self._vertices:
            # Translate to origin
            x_rel = x - cx
            y_rel = y - cy

            # Rotate
            x_new = x_rel * cos_a - y_rel * sin_a
            y_new = x_rel * sin_a + y_rel * cos_a

            # Translate back
            rotated.append((x_new + cx, y_new + cy))

        return VertexLoop(rotated, self._closed)
