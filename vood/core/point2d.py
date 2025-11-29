from __future__ import annotations
from dataclasses import dataclass
from typing import  Iterator

import math


@dataclass(slots=True)
class Point2D:
    """
    A single point in 2D space (mutable and memory efficient).
    Optimized for heavy interpolation via in-place operations.
    """

    x: float
    y: float

    def __iter__(self) -> Iterator[float]:
        """Allows direct unpacking: x, y = point"""
        yield self.x
        yield self.y

    def distance_to(self, other: Point2D) -> float:
        """Calculate Euclidean distance to another point using math.hypot."""
        return math.hypot(self.x - other.x, self.y - other.y)

    # -------------------------------------------------------------
    # IN-PLACE (MUTABLE) OPERATORS (Use for maximum performance)
    # -------------------------------------------------------------
    def __iadd__(self, other: Point2D) -> Point2D:
        """In-place addition: self += other"""
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: Point2D) -> Point2D:
        """In-place subtraction: self -= other"""
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, scalar: float) -> Point2D:
        """In-place scalar multiplication: self *= scalar"""
        self.x *= scalar
        self.y *= scalar
        return self

    def __itruediv__(self, scalar: float) -> Point2D:
        """In-place scalar division: self /= scalar"""
        if scalar == 0.0:
            raise ZeroDivisionError("Cannot divide Point2D by zero scalar.")
        self.x /= scalar
        self.y /= scalar
        return self

    def ilerp(self, p2: Point2D, t: float) -> Point2D:
        """In-place linear interpolation: self becomes the interpolated point."""
        self.x = _lerp(self.x, p2.x, t)
        self.y = _lerp(self.y, p2.y, t)
        return self

    # -------------------------------------------------------------
    # IMMUTABLE OPERATORS (Return a NEW object)
    # -------------------------------------------------------------
    def __add__(self, other: Point2D) -> Point2D:
        """Add two points (vector addition)"""
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point2D) -> Point2D:
        """Subtract two points (vector subtraction)"""
        return Point2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Point2D:
        """Multiply point by scalar"""
        return Point2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Point2D:
        """Divide point by scalar"""
        if scalar == 0.0:
            raise ZeroDivisionError("Cannot divide Point2D by zero scalar.")
        return Point2D(self.x / scalar, self.y / scalar)

    def __rmul__(self, scalar: float) -> Point2D:
        """Reverse multiply point by scalar (e.g., 2.0 * point)"""
        return self * scalar

    def lerp(self, p2: Point2D, t: float) -> Point2D:
        """Linear interpolation between two points (returns a NEW point)"""
        return Point2D(x=_lerp(self.x, p2.x, t), y=_lerp(self.y, p2.y, t))


Points2D = list[Point2D]


# -------------------------------------------------
# POINT POOL
# -------------------------------------------------
class Point2DPool:
    __slots__ = ("pool", "size", "index")

    def __init__(self, size: int):
        # Preallocate pool with Point2D objects
        self.pool = [Point2D(0.0, 0.0) for _ in range(size)]
        self.size = size
        self.index = 0

    def reset(self):
        """Mark all objects reusable for the next cycle."""
        self.index = 0

    def get(self) -> Point2D:
        """Retrieves and resets the next available Point2D instance."""
        i = self.index

        # Check if we need to grow the pool
        if i >= self.size:
            # Out of space → grow (double)
            old_size = self.size
            new_size = old_size * 2

            # Append new Point2D instances
            self.pool.extend(Point2D(0.0, 0.0) for _ in range(old_size))
            self.size = new_size

        # Increment index and retrieve the point
        self.index = i + 1
        point = self.pool[i]

        point.x = 0.0
        point.y = 0.0

        return point


# ❗ Private global pool
_POINT_POOL = Point2DPool(4096)


def new_point2d(x: float, y: float) -> Point2D:
    """Fast pooled point creation."""
    p = _POINT_POOL.get()
    p.x = x
    p.y = y
    return p


def _reset_point2d_pool() -> None:
    """Internal — called once per frame by the animation loop."""
    _POINT_POOL.reset()


def _lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation"""
    return a + (b - a) * t
