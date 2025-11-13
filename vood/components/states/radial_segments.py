"""RadialSegmentsRenderer: draws radial line segments from a center point."""


from typing import List, Tuple, Optional
from dataclasses import dataclass, field

from .base import State
from vood.utils.colors import hex_to_color, to_rgb_string


@dataclass
class RadialSegmentsState(State):
    num_lines: int = 8
    segments: object = field(default_factory=list)
    # segments can be:
    # - List[Tuple[float, float]]: shared by all angles
    # - List[List[Tuple[float, float]]]: per angle
    angles: Optional[List[float]] = None  # Optional custom angles in degrees
    stroke_color: Optional[Tuple[int, int, int]] = (0, 0, 0)
    stroke_width: float = 1.0
    segments_fn: Optional[callable] = None

    def __post_init__(self):

        if isinstance(self.stroke_color, str):
            self.stroke_color = hex_to_color(self.stroke_color)
