from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

from vood.transitions import easing
from vood.core.color import Color
from .morph_base import MorphBaseState


@dataclass(frozen=True)
class MorphTriangleState(MorphBaseState):
    """Equilateral triangle with vertices distributed along perimeter"""

    size: float = 50  # Distance from center to vertex
    fill_color: Optional[Color] = Color(100, 150, 255)
    stroke_color: Optional[Color] = Color.NONE
    stroke_width: float = 2

    DEFAULT_EASING = {
        **MorphBaseState.DEFAULT_EASING,
        "size": easing.in_out,
        "fill_color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        super().__post_init__()
        self._normalize_color_field("fill_color")
        self._normalize_color_field("stroke_color")

    def get_vertices(self) -> List[Tuple[float, float]]:
        """Generate triangle vertices distributed along perimeter

        Triangle points upward with vertices at:
        - Top: 0° (North/straight up)
        - Bottom-right: 120°
        - Bottom-left: 240°
        """
        # Calculate triangle vertices (pointing up, Vood coordinate system)
        triangle_verts = []
        for i in range(3):
            angle = math.radians(i * 120)  # 0°, 120°, 240°
            triangle_verts.append(
                (self.size * math.sin(angle), -self.size * math.cos(angle))
            )

        # Calculate perimeter lengths between vertices
        def distance(p1, p2):
            return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

        edge_lengths = [
            distance(triangle_verts[i], triangle_verts[(i + 1) % 3]) for i in range(3)
        ]
        total_perimeter = sum(edge_lengths)

        # Distribute num_points along the perimeter
        vertices = []
        current_edge = 0
        distance_along_edge = 0

        for i in range(self.num_points):
            # Target distance along total perimeter
            target_distance = (i / self.num_points) * total_perimeter

            # Find which edge we're on
            cumulative = 0
            for edge_idx in range(3):
                if cumulative + edge_lengths[edge_idx] >= target_distance:
                    current_edge = edge_idx
                    distance_along_edge = target_distance - cumulative
                    break
                cumulative += edge_lengths[edge_idx]

            # Interpolate along current edge
            v1 = triangle_verts[current_edge]
            v2 = triangle_verts[(current_edge + 1) % 3]
            t = distance_along_edge / edge_lengths[current_edge]

            x = v1[0] + t * (v2[0] - v1[0])
            y = v1[1] + t * (v2[1] - v1[1])
            vertices.append((x, y))

        return vertices
