"""Perforated primitive renderer - SVG primitive-based for static/keystate rendering"""

from __future__ import annotations
from typing import Optional
import drawsvg as dw
import math

from .base import Renderer
from ..registry import register_renderer
from ..state.perforated.base import (
    PerforatedVertexState, Shape, Circle, Ellipse,
    Rectangle, Polygon, Star, Astroid
)


@register_renderer(PerforatedVertexState)
class PerforatedPrimitiveRenderer(Renderer):
    """Renderer for perforated shape elements using SVG primitives

    Works with all PerforatedXState classes (PerforatedCircle, PerforatedStar, etc.)
    by converting their vertex-based outer contours to SVG paths.

    Uses evenodd fill-rule with SVG paths for clean, high-quality rendering.
    Renders any outer shape with multiple holes of any shape at different
    positions, sizes, and rotations.

    This is used for static rendering and at keystate endpoints (t=0, t=1).
    During morphing (0 < t < 1), the VertexRenderer is used instead to enable
    smooth transitions between different shapes.
    """

    def _render_core(
        self, state: PerforatedVertexState, drawing: Optional[dw.Drawing] = None
    ) -> dw.Group:
        """Render perforated shape using SVG path primitives with evenodd fill-rule"""

        group = dw.Group()

        # Create a path that defines the perforated shape using even-odd fill rule
        path = dw.Path(
            fill=state.fill_color.to_rgb_string() if state.fill_color else "none",
            fill_opacity=state.fill_opacity,
            fill_rule="evenodd",
            stroke=(
                state.stroke_color.to_rgb_string()
                if state.stroke_color and state.stroke_width > 0
                else "none"
            ),
            stroke_width=(
                state.stroke_width
                if state.stroke_color and state.stroke_width > 0
                else 0
            ),
            stroke_opacity=(
                state.stroke_opacity
                if state.stroke_color and state.stroke_width > 0
                else 0
            ),
            stroke_linejoin="round",
            stroke_linecap="round",
        )

        # Draw outer shape (clockwise for outer boundary)
        # Get the outer contour from the state's _generate_outer_contour() method
        outer_contour = state._generate_outer_contour()
        self._add_vertex_loop_to_path(path, outer_contour.vertices, clockwise=True)

        # Draw hole shapes (counter-clockwise - creates holes due to even-odd rule)
        for hole_shape in state.holes:
            self._add_shape_to_path(path, hole_shape, clockwise=False)

        group.append(path)
        return group

    def _add_vertex_loop_to_path(
        self, path: dw.Path, vertices: list, clockwise: bool
    ):
        """Add a vertex loop to the path

        Args:
            path: The path to add vertices to
            vertices: List of (x, y) tuples
            clockwise: If True, draw clockwise; if False, reverse order
        """
        if not vertices or len(vertices) < 2:
            return

        verts = list(vertices)
        if not clockwise:
            verts = verts[::-1]

        # Start at first vertex
        path.M(*verts[0])

        # Draw lines to remaining vertices
        for vertex in verts[1:-1]:  # Skip last vertex (should equal first for closed loop)
            path.L(*vertex)

        path.Z()

    def _add_shape_to_path(self, path: dw.Path, shape: Shape, clockwise: bool):
        """Add a shape to the path by working directly with the Shape object

        Args:
            path: The path to add the shape to
            shape: Shape object (Circle, Ellipse, Rectangle, etc.)
            clockwise: If True, draw clockwise; if False, draw counter-clockwise
        """

        if isinstance(shape, Circle):
            self._add_circle(path, shape.x, shape.y, shape.radius, clockwise)

        elif isinstance(shape, Ellipse):
            self._add_ellipse(
                path, shape.x, shape.y, shape.rx, shape.ry, shape.rotation, clockwise
            )

        elif isinstance(shape, Rectangle):
            self._add_rectangle(
                path, shape.x, shape.y, shape.width, shape.height, shape.rotation, clockwise
            )

        elif isinstance(shape, Polygon):
            self._add_polygon(
                path, shape.x, shape.y, shape.radius, shape.num_sides, shape.rotation, clockwise
            )

        elif isinstance(shape, Star):
            self._add_star(
                path, shape.x, shape.y, shape.outer_radius, shape.inner_radius,
                shape.num_points, shape.rotation, clockwise
            )

        elif isinstance(shape, Astroid):
            self._add_astroid(
                path, shape.x, shape.y, shape.radius, shape.num_cusps,
                shape.curvature, shape.rotation, clockwise
            )

        else:
            raise ValueError(f"Unsupported shape type: {type(shape).__name__}")

    def _add_circle(
        self, path: dw.Path, cx: float, cy: float, radius: float, clockwise: bool
    ):
        """Add a circle to path using arc commands"""
        path.M(cx + radius, cy)
        sweep_flag = 1 if clockwise else 0
        path.A(radius, radius, 0, 0, sweep_flag, cx - radius, cy)
        path.A(radius, radius, 0, 0, sweep_flag, cx + radius, cy)
        path.Z()

    def _add_rectangle(
        self,
        path: dw.Path,
        cx: float,
        cy: float,
        width: float,
        height: float,
        rotation: float,
        clockwise: bool,
    ):
        """Add a rectangle to path"""
        half_w, half_h = width / 2, height / 2
        corners = [
            (-half_w, -half_h),
            (half_w, -half_h),
            (half_w, half_h),
            (-half_w, half_h),
        ]

        # Apply rotation if specified
        if rotation != 0:
            angle_rad = math.radians(rotation)
            cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
            corners = [
                (x * cos_a - y * sin_a + cx, x * sin_a + y * cos_a + cy)
                for x, y in corners
            ]
        else:
            corners = [(x + cx, y + cy) for x, y in corners]

        # Draw rectangle
        if not clockwise:
            corners = corners[::-1]  # Reverse for counter-clockwise

        path.M(*corners[0])
        for corner in corners[1:]:
            path.L(*corner)
        path.Z()

    def _add_ellipse(
        self,
        path: dw.Path,
        cx: float,
        cy: float,
        rx: float,
        ry: float,
        rotation: float,
        clockwise: bool,
    ):
        """Add an ellipse to path using arc commands"""
        if clockwise:
            # Clockwise: start right, go down, left, up, back to right
            path.M(cx + rx, cy)
            path.A(rx, ry, rotation, 0, 1, cx, cy + ry)
            path.A(rx, ry, rotation, 0, 1, cx - rx, cy)
            path.A(rx, ry, rotation, 0, 1, cx, cy - ry)
            path.A(rx, ry, rotation, 0, 1, cx + rx, cy)
        else:
            # Counter-clockwise: start right, go up, left, down, back to right
            path.M(cx + rx, cy)
            path.A(rx, ry, rotation, 0, 0, cx, cy - ry)
            path.A(rx, ry, rotation, 0, 0, cx - rx, cy)
            path.A(rx, ry, rotation, 0, 0, cx, cy + ry)
            path.A(rx, ry, rotation, 0, 0, cx + rx, cy)
        path.Z()

    def _add_polygon(
        self,
        path: dw.Path,
        cx: float,
        cy: float,
        size: float,
        num_sides: int,
        rotation: float,
        clockwise: bool,
    ):
        """Add a regular polygon to path"""
        corners = []
        for i in range(num_sides):
            angle = math.radians(i * (360 / num_sides) - 90 + rotation)
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            corners.append((x, y))

        if not clockwise:
            corners = corners[::-1]

        path.M(*corners[0])
        for corner in corners[1:]:
            path.L(*corner)
        path.Z()

    def _add_star(
        self,
        path: dw.Path,
        cx: float,
        cy: float,
        outer_radius: float,
        inner_radius: float,
        num_points: int,
        rotation: float,
        clockwise: bool,
    ):
        """Add a star to path with alternating outer and inner vertices"""
        corners = []
        for i in range(num_points * 2):
            angle = math.radians(i * (360 / (num_points * 2)) - 90 + rotation)
            # Alternate between outer and inner radius
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            corners.append((x, y))

        if not clockwise:
            corners = corners[::-1]

        path.M(*corners[0])
        for corner in corners[1:]:
            path.L(*corner)
        path.Z()

    def _add_astroid(
        self,
        path: dw.Path,
        cx: float,
        cy: float,
        radius: float,
        num_cusps: int,
        curvature: float,
        rotation: float,
        clockwise: bool,
    ):
        """Add an astroid to path using quadratic Bezier curves"""
        # Calculate cusp positions (the pointed tips)
        cusps = []
        for i in range(num_cusps):
            angle = math.radians(i * (360 / num_cusps) - 90 + rotation)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            cusps.append((x, y))

        if not clockwise:
            cusps = cusps[::-1]

        # Start at first cusp
        path.M(*cusps[0])

        # Draw curves connecting cusps
        for i in range(num_cusps):
            start_cusp = cusps[i]
            end_cusp = cusps[(i + 1) % num_cusps]

            # Calculate control point for inward-bending curve
            mid_x = (start_cusp[0] + end_cusp[0]) / 2
            mid_y = (start_cusp[1] + end_cusp[1]) / 2

            # Pull control point toward center based on curvature
            control_x = mid_x + (cx - mid_x) * curvature
            control_y = mid_y + (cy - mid_y) * curvature

            # Draw quadratic Bezier curve to next cusp
            path.Q(control_x, control_y, *end_cusp)

        path.Z()
