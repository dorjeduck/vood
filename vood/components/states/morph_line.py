from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

from vood.transitions import easing
from .morph_base import MorphBaseState
from vood.core import Color


@dataclass(frozen=True)
class MorphLineState(MorphBaseState):
    """Straight line with vertices distributed along its length

    Note: Lines are open shapes (closed=False by default).
    When morphing into closed shapes, the endpoints will be connected
    for fill area determination.
    """

    length: float = 100
    closed: bool = False  # Lines are open by default
    stroke_color: Optional[Color] = Color(0, 0, 0)
    stroke_width: float = 2

    DEFAULT_EASING = {
        **MorphBaseState.DEFAULT_EASING,
        "length": easing.in_out,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        super().__post_init__()
        self._normalize_color_field("stroke_color")

    def get_vertices(self) -> List[Tuple[float, float]]:
        """Generate line vertices from -length/2 to +length/2 along x-axis"""
        half_length = self.length / 2
        return [
            (-half_length + (i / (self.num_points - 1)) * self.length, 0)
            for i in range(self.num_points)
        ]
