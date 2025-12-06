"""RadialSegmentsRenderer: draws radial line segments from a center point."""

from typing import List, Tuple, Optional
from dataclasses import dataclass, field

from vood.component.state.base_color import ColorState

from .base import State
from vood.component.registry import renderer
from vood.component.renderer.radial_segments import RadialSegmentsRenderer
from vood.core.color import Color


@renderer(RadialSegmentsRenderer)
@dataclass(frozen=True)
class RadialSegmentsState(ColorState):
    num_lines: int = 8
    segments: object = field(default_factory=list)
    # segments can be:
    # - Points2D: shared by all angles
    # - List[Points2D]: per angle
    angles: Optional[List[float]] = None  # Optional custom angles in degrees
    segments_fn: Optional[callable] = None
