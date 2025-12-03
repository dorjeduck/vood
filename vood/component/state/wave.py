from __future__ import annotations
import math
from dataclasses import dataclass

from vood.transition import easing
from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours
from vood.core.point2d import Point2D
from vood.component.registry import renderer
from vood.component.renderer.wave import WaveRenderer
from vood.component.state.line import line_endpoints_to_center_rotation_length

@renderer(WaveRenderer)
@dataclass(frozen=True)
class WaveState(VertexState):
    """Sine wave - OPEN shape"""

    length: float = 100
    amplitude: float = 20
    frequency: float = 2  # Number of complete waves
    closed: bool = False

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "length": easing.in_out,
        "amplitude": easing.in_out,
        "frequency": easing.in_out,
    }

    @staticmethod
    def from_endpoints(
        x1:float,y1:float,x2:float,y2:float,
        amplitude:float,
        frequency:float,
        scale:Optional[float]=None,
        opacity:Optional[float]=None,
    )-> WaveState:
        cx, cy, calc_rotation, length =  line_endpoints_to_center_rotation_length(x1,y1,x2,y2)
        return WaveState(
            x=cx,
            y=cy,
            rotation=calc_rotation,
            length=length,
            amplitude=amplitude,
            frequency=frequency,
            scale=scale,
            opacity=opacity,
        )

    def _generate_contours(self) -> VertexContours:
        """Generate wave vertices"""
        vertices = []
        half_length = self.length / 2

        for i in range(self._num_vertices):
            t = i / (self._num_vertices - 1) if self._num_vertices > 1 else 0
            x = -half_length + t * self.length
            y = self.amplitude * math.sin(t * self.frequency * 2 * math.pi)
            vertices.append(Point2D(x, y))

        return VertexContours.from_single_loop(vertices, closed=self.closed)
