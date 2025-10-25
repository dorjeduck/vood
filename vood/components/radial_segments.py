"""RadialSegmentsRenderer: draws radial line segments from a center point."""

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
import drawsvg as dw
from vood.components import Renderer, State
from vood.utils.colors import to_rgb_string


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


class RadialSegmentsRenderer(Renderer):

    def _render_core(self, state: RadialSegmentsState) -> dw.Group:
        """
        Render radial line segments centered at origin (0,0).
        Each line is made of segments defined by (from_px, to_px) tuples.
        Returns a drawsvg Group containing all lines.
        """

        angles = state.angles[: state.num_lines] or [
            i * 360 / state.num_lines for i in range(state.num_lines)
        ]

        group = dw.Group()
        stroke = to_rgb_string(state.stroke_color) if state.stroke_color else "black"

        for idx, angle in enumerate(angles):
            # Make 0 degrees point north and 90 east
            rad = math.radians(angle - 90)
            segs = None
            segments = state.segments
            # Determine base_segments for this index
            if isinstance(segments, list):
                if (
                    segments
                    and isinstance(segments[0], (tuple, list))
                    and len(segments) > 0
                    and isinstance(segments[0][0], (int, float))
                ):
                    # Shared segments for all angles
                    base_segments = segments
                elif segments and isinstance(segments[0], list):
                    # Per-angle segments
                    base_segments = segments[idx] if idx < len(segments) else []
                else:
                    base_segments = []
            else:
                base_segments = []

            if state.segments_fn:
                segs = state.segments_fn(idx, base_segments)
            else:
                segs = base_segments

            if segs:
                for from_px, to_px in segs:
                    x1 = from_px * math.cos(rad)
                    y1 = from_px * math.sin(rad)
                    x2 = to_px * math.cos(rad)
                    y2 = to_px * math.sin(rad)
                    line = dw.Line(
                        x1,
                        y1,
                        x2,
                        y2,
                        stroke=stroke,
                        stroke_width=state.stroke_width,
                    )
                    group.append(line)

        return group
