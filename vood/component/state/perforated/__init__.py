"""Perforated shapes submodule - shapes with holes"""

from .base import (
    PerforatedVertexState,
    Shape,
    Circle,
    Ellipse,
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
    # Shape helper classes (for specifying holes)
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
