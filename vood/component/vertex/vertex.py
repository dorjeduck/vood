"""Single vertex (point) class"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Vertex:
    """A single point in 2D space

    Very general base class representing a vertex with x and y coordinates.
    """

    x: float
    y: float

    def as_tuple(self) -> Tuple[float, float]:
        """Return vertex as (x, y) tuple"""
        return (self.x, self.y)

    def distance_to(self, other: Vertex) -> float:
        """Calculate Euclidean distance to another vertex"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __add__(self, other: Vertex) -> Vertex:
        """Add two vertices (vector addition)"""
        return Vertex(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vertex) -> Vertex:
        """Subtract two vertices (vector subtraction)"""
        return Vertex(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vertex:
        """Multiply vertex by scalar"""
        return Vertex(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Vertex:
        """Divide vertex by scalar"""
        return Vertex(self.x / scalar, self.y / scalar)
