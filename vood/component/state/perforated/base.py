"""Base classes for perforated shapes - shapes with holes"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from vood.component.state.base import State
from vood.component.state.base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexLoop
from vood.core.color import Color
from vood.transition import easing
from vood.core.point2d import Point2D


# ============================================================================
# Base Perforated State Class
# ============================================================================


@dataclass(frozen=True)
class PerforatedVertexState(VertexState):
    """Base class for all perforated shapes (shapes with holes)

    Perforated shapes have an outer contour (defined by subclass) and
    zero or more vertex loops (specified via Shape objects).

    Subclasses implement _generate_outer_contour() to define their specific
    outer shape geometry (circle, star, ellipse, etc.).

    Visual properties (fill_color, stroke_color, etc.) are inherited from
    VertexState and apply to the entire perforated shape uniformly.

    Args:
        holes: List of Shape objects specifying hole geometry and positions

    Example:
        PerforatedCircleState(
            radius=100,
            holes=[
                Circle(radius=20, x=-30, y=0),
                Star(outer_radius=15, inner_radius=7, num_points=5, x=30, y=0),
            ],
            fill_color=Color("#4ECDC4"),
            stroke_color=Color("#FFFFFF"),
        )
    """

    holes: List[Shape] = field(default_factory=list)

    holes_fill_color: Optional[Color] = Color.NONE
    holes_fill_opacity: Optional[float] = 0

    holes_stroke_color: Optional[Color] = Color.NONE
    holes_stroke_opacity: Optional[float] = None
    holes_stroke_width: Optional[float] = None

    # Mark vertex loops as non-interpolatable (structural property)
    NON_INTERPOLATABLE_FIELDS = frozenset(
        ["holes", "NON_INTERPOLATABLE_FIELDS", "DEFAULT_EASING"]
    )

    DEFAULT_EASING = {
        **VertexState.DEFAULT_EASING,
        "holes_fill_color": easing.linear,
        "holes_fill_opacity": easing.linear,
        "holes_stroke_color": easing.linear,
        "holes_stroke_opacity": easing.linear,
        "holes_stroke_width": easing.linear,
    }

    def __post_init__(self):
        super().__post_init__()

        if self.holes_stroke_color is Color.NONE:
            self._set_field("holes_stroke_color", self.stroke_color)
        if self.holes_stroke_opacity is None:
            self._set_field("holes_stroke_opacity", self.stroke_opacity)
        if self.holes_stroke_width is None:
            self._set_field("holes_stroke_width", self.stroke_width)

    @abstractmethod
    def _generate_outer_contour(self) -> VertexLoop:
        """Generate the outer shape contour (subclasses implement this)

        Returns:
            VertexLoop for the outer shape, centered at origin (0, 0)
        """
        raise NotImplementedError

    def _generate_contours(self) -> VertexContours:
        """Generate perforated shape contours (outer + holes)

        Returns VertexContours with:
        - Outer: shape specified by subclass (counter-clockwise)
        - holes: list of shapes specified by vertex loops field (clockwise)
        """
        # Generate outer shape (counter-clockwise winding)
        outer = self._generate_outer_contour()

        # Generate hole shapes (clockwise winding for holes)
        holes = []
        for hole_shape in self.holes:
            hole_loop = self._shape_to_loop(hole_shape)
            # Reverse for clockwise winding (creates hole in rendering)
            holes.append(hole_loop.reverse())

        return VertexContours(outer=outer, holes=holes)

    def _shape_to_loop(self, shape: Shape) -> VertexLoop:
        """Convert a Shape object to a VertexLoop

        Args:
            shape: Shape object (Circle, Ellipse, Rectangle, etc.)

        Returns:
            VertexLoop for the specified shape at specified position
        """
        from vood.component.vertex import (
            VertexCircle,
            VertexEllipse,
            VertexRectangle,
            VertexSquare,
            VertexTriangle,
            VertexRegularPolygon,
            VertexStar,
            VertexAstroid,
            rotate_vertices,
        )

        if isinstance(shape, Circle):
            return VertexCircle(
                cx=shape.x,
                cy=shape.y,
                radius=shape.radius,
                num_vertices=self._num_vertices,
            )

        elif isinstance(shape, Ellipse):
            loop = VertexEllipse(
                cx=shape.x,
                cy=shape.y,
                rx=shape.rx,
                ry=shape.ry,
                num_vertices=self._num_vertices,
            )
            if shape.rotation != 0:
                # Rotate around the shape's center by translating to origin, rotating, translating back
                translated = [
                    Point2D(x - shape.x, y - shape.y) for x, y in loop.vertices
                ]
                rotated = rotate_vertices(translated, shape.rotation)
                final = [Point2D(x + shape.x, y + shape.y) for x, y in rotated]
                return VertexLoop(final, closed=True)
            return loop

        elif isinstance(shape, Rectangle):
            loop = VertexRectangle(
                cx=shape.x,
                cy=shape.y,
                width=shape.width,
                height=shape.height,
                num_vertices=self._num_vertices,
            )
            if shape.rotation != 0:
                # Rotate around the shape's center by translating to origin, rotating, translating back
                translated = [(x - shape.x, y - shape.y) for x, y in loop.vertices]
                rotated = rotate_vertices(translated, shape.rotation)
                final = [Point2D(x + shape.x, y + shape.y) for x, y in rotated]
                return VertexLoop(final, closed=True)
            return loop

        elif isinstance(shape, Square):
            loop = VertexSquare(
                cx=shape.x,
                cy=shape.y,
                size=shape.size,
                num_vertices=self._num_vertices,
            )
            if shape.rotation != 0:
                # Rotate around the shape's center by translating to origin, rotating, translating back
                translated = [(x - shape.x, y - shape.y) for x, y in loop.vertices]
                rotated = rotate_vertices(translated, shape.rotation)
                final = [Point2D(x + shape.x, y + shape.y) for x, y in rotated]
                return VertexLoop(final, closed=True)
            return loop

        elif isinstance(shape, Polygon):
            return VertexRegularPolygon(
                cx=shape.x,
                cy=shape.y,
                size=shape.radius,
                num_sides=shape.num_sides,
                num_vertices=self._num_vertices,
                rotation=shape.rotation,
            )

        elif isinstance(shape, Star):
            loop = VertexStar(
                cx=shape.x,
                cy=shape.y,
                outer_radius=shape.outer_radius,
                inner_radius=shape.inner_radius,
                num_points=shape.num_points,
                num_vertices=self._num_vertices,
            )
            if shape.rotation != 0:
                # Rotate around the shape's center by translating to origin, rotating, translating back
                translated = [(x - shape.x, y - shape.y) for x, y in loop.vertices]
                rotated = rotate_vertices(translated, shape.rotation)
                final = [Point2D(x + shape.x, y + shape.y) for x, y in rotated]
                return VertexLoop(final, closed=True)
            return loop

        elif isinstance(shape, Astroid):
            loop = VertexAstroid(
                cx=shape.x,
                cy=shape.y,
                radius=shape.radius,
                num_cusps=shape.num_cusps,
                curvature=shape.curvature,
                num_vertices=self._num_vertices,
            )
            if shape.rotation != 0:
                # Rotate around the shape's center by translating to origin, rotating, translating back
                translated = [(x - shape.x, y - shape.y) for x, y in loop.vertices]
                rotated = rotate_vertices(translated, shape.rotation)
                final = [Point2D(x + shape.x, y + shape.y) for x, y in rotated]
                return VertexLoop(final, closed=True)
            return loop

        else:
            raise ValueError(
                f"Unsupported shape type: {type(shape).__name__}. "
                f"Supported: Circle, Ellipse, Rectangle, Polygon, Star, Astroid"
            )

    @staticmethod
    def get_renderer_class():
        """Get the primitive renderer for static/keystate rendering"""
        from vood.component.renderer.perforated_primitive import (
            PerforatedPrimitiveRenderer,
        )

        return PerforatedPrimitiveRenderer

    @staticmethod
    def get_vertex_renderer_class():
        """Get the vertex renderer for morphing transitions"""
        from vood.component.renderer.base_vertex import VertexRenderer

        return VertexRenderer


# ============================================================================
# Shape Helper Classes - for specifying hole geometry and position
# ============================================================================


@dataclass(frozen=True)
class Shape(ABC):
    """Base class for shape specifications (used for holes)

    Shapes specify geometry and position but not visual properties.
    Visual properties (fill, stroke, etc.) come from the parent PerforatedXState.

    Args:
        x: X position relative to element center
        y: Y position relative to element center
        rotation: Rotation in degrees (clockwise)
    """

    x: float = 0
    y: float = 0
    rotation: float = 0
    stroke_opacity = 0.5


@dataclass(frozen=True)
class Circle(Shape):
    """Circular shape specification

    Args:
        radius: Circle radius
        x: X position (default 0)
        y: Y position (default 0)
        rotation: Rotation in degrees (has no visual effect for circles)
    """

    radius: float = 10


@dataclass(frozen=True)
class Ellipse(Shape):
    """Elliptical shape specification

    Args:
        rx: Horizontal radius (semi-major axis)
        ry: Vertical radius (semi-minor axis)
        x: X position (default 0)
        y: Y position (default 0)
        rotation: Rotation in degrees
    """

    rx: float = 10
    ry: float = 10


@dataclass(frozen=True)
class Rectangle(Shape):
    """Rectangular shape specification

    Args:
        width: Rectangle width
        height: Rectangle height
        x: X position (default 0)
        y: Y position (default 0)
        rotation: Rotation in degrees
    """

    width: float = 20
    height: float = 20


@dataclass(frozen=True)
class Square(Shape):
    """Rectangular shape specification

    Args:
        size: Square width and height
        x: X position (default 0)
        y: Y position (default 0)
        rotation: Rotation in degrees
    """

    size: float = 20


@dataclass(frozen=True)
class Polygon(Shape):
    """Regular polygon shape specification

    Args:
        num_sides: Number of sides (3 = triangle, 5 = pentagon, etc.)
        radius: Radius of circumscribed circle
        x: X position (default 0)
        y: Y position (default 0)
        rotation: Rotation in degrees
    """

    num_sides: int = 5
    radius: float = 10

    def __post_init__(self):
        """Validate number of sides"""
        if self.num_sides < 3:
            raise ValueError(
                f"Polygon must have at least 3 sides, got {self.num_sides}"
            )


@dataclass(frozen=True)
class Star(Shape):
    """Star shape specification

    Args:
        num_points: Number of star points
        outer_radius: Radius of outer points
        inner_radius: Radius of inner points
        x: X position (default 0)
        y: Y position (default 0)
        rotation: Rotation in degrees
    """

    num_points: int = 5
    outer_radius: float = 10
    inner_radius: float = 5

    def __post_init__(self):
        """Validate star parameters"""
        if self.num_points < 3:
            raise ValueError(f"Star must have at least 3 points, got {self.num_points}")
        if self.inner_radius >= self.outer_radius:
            raise ValueError(
                f"inner_radius ({self.inner_radius}) must be less than "
                f"outer_radius ({self.outer_radius})"
            )


@dataclass(frozen=True)
class Astroid(Shape):
    """Astroid shape specification (star-like with curved indentations)

    Args:
        radius: Radius of the astroid
        num_cusps: Number of cusps (pointed tips)
        curvature: How much the sides curve inward (0.0-1.0, where 1.0 is maximum curve)
        x: X position (default 0)
        y: Y position (default 0)
        rotation: Rotation in degrees
    """

    radius: float = 50
    num_cusps: int = 4
    curvature: float = 0.7

    def __post_init__(self):
        """Validate astroid parameters"""
        if self.num_cusps < 3:
            raise ValueError(
                f"Astroid must have at least 3 cusps, got {self.num_cusps}"
            )
        if not 0.0 <= self.curvature <= 1.0:
            raise ValueError(
                f"curvature must be between 0.0 and 1.0, got {self.curvature}"
            )
