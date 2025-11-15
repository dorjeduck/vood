from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

from vood.transitions import easing
from vood.core.color import Color

from .morph_base import MorphBaseState


@dataclass(frozen=True)
class MorphCircleState(MorphBaseState):
    """Circle with evenly distributed vertices"""

    radius: float = 50
    fill_color: Optional[Color] = Color(100, 150, 255)
    stroke_color: Optional[Color] = Color.NONE
    stroke_width: float = 2

    DEFAULT_EASING = {
        **MorphBaseState.DEFAULT_EASING,
        "radius": easing.in_out,
        "fill_color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        super().__post_init__()
        self._normalize_color_field("fill_color")
        self._normalize_color_field("stroke_color")

    def get_vertices(self) -> List[Tuple[float, float]]:
        """Generate circle vertices, starting at 0° (North/top) going clockwise"""
        return [
            (
                self.radius * math.sin(2 * math.pi * i / self.num_points),
                -self.radius * math.cos(2 * math.pi * i / self.num_points),
            )
            for i in range(self.num_points)
        ]
