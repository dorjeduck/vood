"""Perforated shapes submodule - shapes with  vertex_loops"""

from .base import (
    PerforatedVertexState,
    Shape,
    Circle,
    Ellipse,
    Square,
    Rectangle,
    Polygon,
    Star,
    Astroid,
)
from .circle import PerforatedCircleState
from .star import PerforatedStarState
from .ellipse import PerforatedEllipseState
from .rectangle import PerforatedRectangleState
from .polygon import PerforatedPolygonState
from .triangle import PerforatedTriangleState

__all__ = [
    # Base class
    "PerforatedVertexState",
    # Shape helper classes (for specifying  vertex_loops )
    "Shape",
    "Circle",
    "Ellipse",
    "Rectangle",
    "Polygon",
    "Star",
    "Astroid",
    # Concrete perforated state classes
    "PerforatedCircleState",
    "PerforatedStarState",
    "PerforatedEllipseState",
    "PerforatedRectangleState",
    "PerforatedPolygonState",
    "PerforatedTriangleState",
]
