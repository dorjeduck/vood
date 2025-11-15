from __future__ import annotations
import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional

import drawsvg as dw

from vood.components.states.base import State
from vood.transitions import easing
from vood.core.color import Color

from vood.transitions.interpolation.morpher.morph_state_interpolation import (
    interpolate_morph_states,
)


@dataclass(frozen=True)
class MorphBaseState(State):
    """Base state for vertex-based morphable shapes

    All morph shapes share:
    - num_points: Resolution (number of vertices)
    - closed: Whether the shape is closed (affects fill)
    - fill_color: Interior color (only for closed shapes)
    - stroke_color: Outline color

    Subclasses override get_vertices() to generate their specific geometry.
    """

    num_points: int = 64  # Vertex resolution - must match for morphing!
    closed: bool = True  # Whether shape is closed

    fill_color: Optional[Color] = Color(100, 150, 255)
    stroke_color: Optional[Color] = Color.NONE
    stroke_width: float = 2

    # Default easing
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "num_points": easing.step,  # Can't smoothly change resolution
        "closed": easing.step,  # Boolean
        "fill_color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    @abstractmethod
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Generate vertices for this shape

        Must return exactly num_points vertices.
        Vertices should be centered at origin (0, 0).
        """
        raise NotImplementedError

    def __post_init__(self):
        """Normalize color fields"""
        self._normalize_color_field("fill_color")
        self._normalize_color_field("stroke_color")
