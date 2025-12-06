from typing import TYPE_CHECKING, Optional

"""RadialSegmentsRenderer: draws radial line segments from a center point."""

import math

import drawsvg as dw
from .base import Renderer

if TYPE_CHECKING:
    from ..state.radial_segments import RadialSegmentsState



class RadialSegmentsRenderer(Renderer):

    def _render_core(
        self, state: "RadialSegmentsState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Group:
        """
        Render radial line segments centered at origin (0,0).
        Each line is made of segments defined by (from_px, to_px) tuples.
        Returns a drawsvg Group containing all lines.
        """

        angles = state.angles[: state.num_lines] or [
            i * 360 / state.num_lines for i in range(state.num_lines)
        ]

        group = dw.Group()
        stroke = state.stroke_color.to_rgb_string() if state.stroke_color else "black"

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
                    line_kwargs = {}
                    self._set_fill_and_stroke_kwargs(state, line_kwargs, drawing)
                    line = dw.Line(x1, y1, x2, y2, **line_kwargs)
                    group.append(line)

        return group
