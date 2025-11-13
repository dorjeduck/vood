"""RadialSegmentsRenderer: draws radial line segments from a center point."""

from typing import List, Tuple, Optional
from dataclasses import dataclass, field

from .base import State
from vood.core.color import Color


@dataclass(frozen=True)
class RadialSegmentsState(State):
    num_lines: int = 8
    segments: object = field(default_factory=list)
    # segments can be:
    # - List[Tuple[float, float]]: shared by all angles
    # - List[List[Tuple[float, float]]]: per angle
    angles: Optional[List[float]] = None  # Optional custom angles in degrees
    stroke_color: Optional[Color] = (255, 0, 0)
    stroke_opacity: float = 1
    stroke_width: float = 1.0
    segments_fn: Optional[callable] = None

    def __post_init__(self):
        self._none_color("stroke_color")

    @staticmethod
    def get_renderer_class():
        from ..renderer.radial_segments import RadialSegmentsRenderer

        return RadialSegmentsRenderer
