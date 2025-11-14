from dataclasses import dataclass

from vood.transitions import easing
from .circle import CircleState


@dataclass
class DoubleCircleState(CircleState):
    distance: float = 0  # Distance between the two circles

    DEFAULT_EASING = {
        **CircleState.DEFAULT_EASING,
        "distance": easing.in_out,
    }
