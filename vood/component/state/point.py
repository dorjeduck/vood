"""Point state for explicit shape disappearance/appearance"""

from dataclasses import dataclass
from vood.component.registry import renderer
from vood.component.vertex.vertex_contours import VertexContours
from vood.component.vertex.vertex_point import VertexPoint
from .base_vertex import VertexState


@renderer("vood.component.renderer.point.PointRenderer")
@dataclass(frozen=True)
class PointState(VertexState):
    """A degenerate state representing a single point

    Used to explicitly control where shapes disappear to or appear from
    during M→N morphing transitions. Unlike implicit zero-states, PointState
    gives users full control over:
    - Exact disappearance location (x, y)
    - Opacity behavior during transition
    - Visual representation (nothing rendered at t=1.0)

    During morphing, shapes smoothly collapse to (or expand from) the point
    location. The opacity can be set to 0.0 for fade-out effects, or 1.0
    to maintain visibility until the final moment.

    Examples:
        # Shape fades out while moving to point
        VElement(keystates=[
            CircleState(x=0, y=0, radius=50),
            PointState(x=100, y=50, opacity=0.0)
        ])

        # Shape stays visible then pops at point
        VElement(keystates=[
            CircleState(x=0, y=0, radius=50),
            PointState(x=100, y=50, opacity=1.0)
        ])

        # Multiple shapes converge to one point
        VElement(keystates=[
            ShapeCollectionState(shapes=[c1, c2, c3]),
            ShapeCollectionState(shapes=[PointState(x=0, y=0)])
        ])

    Attributes:
        x: X coordinate of the point
        y: Y coordinate of the point
        opacity: Opacity at the point (0.0 = fade out, 1.0 = visible until end)
        num_vertices: Number of vertices in degenerate loop (default 128 to match other shapes)
    """

    num_vertices: int = 128  # Number of vertices (all at same location, matches other shapes)

    def _generate_contours(self) -> VertexContours:
        """Generate degenerate contour (all vertices at same point)"""
        point = VertexPoint(cx=0, cy=0, num_vertices=self.num_vertices)
        return VertexContours(outer=point, holes=None)
