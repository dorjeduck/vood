from __future__ import annotations
from .base import State
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional

from vood.transitions import easing
from vood.core.color import Color


@dataclass(frozen=True)
class MorphBaseState(State):
    """Base state for vertex-based morphable shapes

    All morph shapes share:
    - num_points: Resolution (number of vertices)
    - closed: Whether the shape is closed (affects fill)

    Subclasses override get_vertices() to generate their specific geometry.
    Subclasses should define their own color properties as needed.
    """

    num_points: int = 64  # Vertex resolution - must match for morphing!
    closed: bool = True  # Whether shape is closed

    # Default easing
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "num_points": easing.step,
        "closed": easing.step,
    }

    @abstractmethod
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Generate vertices for this shape

        Must return exactly num_points vertices.
        Vertices should be centered at origin (0, 0).
        """
        raise NotImplementedError


@dataclass(frozen=True)
class MorphRawState(MorphBaseState):
    """Raw morph state holding pre-computed aligned vertices

    This is created internally during morph preprocessing.
    Users should not create this directly.
    """

    vertices: List[Tuple[float, float]] = None
    fill_color: Optional[Color] = None
    stroke_color: Optional[Color] = None
    stroke_width: float = 2

    DEFAULT_EASING = {
        **MorphBaseState.DEFAULT_EASING,
        "vertices": easing.linear,  # Vertices interpolate linearly
        "fill_color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        super().__post_init__()
        if hasattr(self, "fill_color") and self.fill_color is not None:
            self._normalize_color_field("fill_color")
        if hasattr(self, "stroke_color") and self.stroke_color is not None:
            self._normalize_color_field("stroke_color")

    def get_vertices(self) -> List[Tuple[float, float]]:
        """Return the pre-computed vertices"""
        return self.vertices if self.vertices else []
