from dataclasses import dataclass, replace
import drawsvg as dw
import sys
import os

from vood.utils.colors import hex_to_color

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vood.transitions import easing
from .circle import CircleState


@dataclass
class DoubleCircleState(CircleState):
    distance: float = 0  # Distance between the two circles

    DEFAULT_EASING = {
        **CircleState.DEFAULT_EASING,
        "distance": easing.in_out,
    }

    def __post_init__(self):
        if isinstance(self.color, str):
            self.color = hex_to_color(self.color)
        if isinstance(self.stroke_color, str):
            self.stroke_color = hex_to_color(self.stroke_color)
