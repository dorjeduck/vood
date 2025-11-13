# ============================================================================
# vood/paths/morphing.py
# ============================================================================
"""
Polymorph-style path morphing implementation

This implements the core algorithm from notoriousb1t/polymorph:
1. Convert all path commands to cubic bezier curves
2. Normalize paths to find optimal starting points
3. Fill paths with duplicate points to equalize lengths
4. Use matrix-based interpolation for smooth morphing

Key insight: Treat paths as sequences of cubic bezier control points,
not as geometric primitives. This makes interpolation trivial.
"""

from __future__ import annotations
from typing import List, Tuple
from dataclasses import dataclass
import math

from vood.path.commands import (
    PathCommand,
    MoveTo,
    LineTo,
    QuadraticBezier,
    CubicBezier,
    ClosePath,
)
from vood.path.svg_path import SVGPath


@dataclass
class Point:
    """Simple 2D point"""

    x: float
    y: float

    def distance_to(self, other: Point) -> float:
        """Euclidean distance to another point"""
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx * dx + dy * dy)


# ============================================================================
# Poly-Bezier Data Structure
# ============================================================================


class PolyBezier:
    """
    Polymorph-style poly-bezier representation

    Data format: [start_x, start_y, c1x, c1y, c2x, c2y, end_x, end_y, ...]
    Each curve is represented by 6 values: 2 control points + end point
    Starting point comes from previous curve's end point (or initial move)
    """

    def __init__(self, data: List[float]):
        self.data = data

    def __len__(self) -> int:
        return len(self.data)

    def get_curve_count(self) -> int:
        """Number of cubic bezier curves in this poly-bezier"""
        return max(0, (len(self.data) - 2) // 6)

    def get_start_point(self) -> Point:
        """Get the starting point of the path"""
        return Point(self.data[0], self.data[1])

    def get_curves(self) -> List[Tuple[Point, Point, Point, Point]]:
        """Get all curves as (start, c1, c2, end) tuples"""
        curves = []
        if len(self.data) < 8:  # Need at least start + one curve
            return curves

        # First curve uses the initial start point
        start = Point(self.data[0], self.data[1])

        for i in range(2, len(self.data), 6):
            if i + 5 >= len(self.data):
                break

            c1 = Point(self.data[i], self.data[i + 1])
            c2 = Point(self.data[i + 2], self.data[i + 3])
            end = Point(self.data[i + 4], self.data[i + 5])

            curves.append((start, c1, c2, end))
            start = end  # Next curve starts where this one ended

        return curves

    def to_svg_path(self) -> SVGPath:
        """Convert back to SVGPath commands"""
        if len(self.data) < 2:
            return SVGPath([])

        commands = [MoveTo(self.data[0], self.data[1])]

        for i in range(2, len(self.data), 6):
            if i + 5 >= len(self.data):
                break

            commands.append(
                CubicBezier(
                    self.data[i],
                    self.data[i + 1],  # c1
                    self.data[i + 2],
                    self.data[i + 3],  # c2
                    self.data[i + 4],
                    self.data[i + 5],  # end
                )
            )

        return SVGPath(commands)


# ============================================================================
# Path to Poly-Bezier Conversion
# ============================================================================


def convert_to_poly_bezier(path: SVGPath) -> PolyBezier:
    """
    Convert an SVGPath to poly-bezier format

    This is the KEY function that makes Polymorph work:
    - Converts all commands to cubic bezier curves
    - Lines become flat curves (control points = start/end)
    - Quadratic curves are elevated to cubic
    - Arcs are approximated with cubic curves
    """

    if not path.commands:
        return PolyBezier([])

    data: List[float] = []
    current_pos = Point(0, 0)
    start_pos = Point(0, 0)

    for cmd in path.commands:
        abs_cmd = cmd.to_absolute((current_pos.x, current_pos.y))

        if isinstance(abs_cmd, MoveTo):
            # Start a new subpath
            current_pos = Point(abs_cmd.x, abs_cmd.y)
            start_pos = current_pos

            # If this is the first command, set the starting point
            if len(data) == 0:
                data.extend([abs_cmd.x, abs_cmd.y])

        elif isinstance(abs_cmd, LineTo):
            # Convert line to flat cubic curve
            # Control points are 1/3 and 2/3 along the line
            c1x = current_pos.x + (abs_cmd.x - current_pos.x) / 3
            c1y = current_pos.y + (abs_cmd.y - current_pos.y) / 3
            c2x = current_pos.x + 2 * (abs_cmd.x - current_pos.x) / 3
            c2y = current_pos.y + 2 * (abs_cmd.y - current_pos.y) / 3

            data.extend([c1x, c1y, c2x, c2y, abs_cmd.x, abs_cmd.y])
            current_pos = Point(abs_cmd.x, abs_cmd.y)

        elif isinstance(abs_cmd, CubicBezier):
            # Already a cubic curve - just add it
            data.extend(
                [
                    abs_cmd.cx1,
                    abs_cmd.cy1,
                    abs_cmd.cx2,
                    abs_cmd.cy2,
                    abs_cmd.x,
                    abs_cmd.y,
                ]
            )
            current_pos = Point(abs_cmd.x, abs_cmd.y)

        elif isinstance(abs_cmd, QuadraticBezier):
            # Convert quadratic to cubic using standard formula
            # For quadratic P0, P1, P2:
            # Cubic control points are P0 + 2/3*(P1-P0) and P2 + 2/3*(P1-P2)
            p0 = current_pos
            p1 = Point(abs_cmd.cx, abs_cmd.cy)
            p2 = Point(abs_cmd.x, abs_cmd.y)

            c1x = p0.x + 2 / 3 * (p1.x - p0.x)
            c1y = p0.y + 2 / 3 * (p1.y - p0.y)
            c2x = p2.x + 2 / 3 * (p1.x - p2.x)
            c2y = p2.y + 2 / 3 * (p1.y - p2.y)

            data.extend([c1x, c1y, c2x, c2y, p2.x, p2.y])
            current_pos = p2

        elif isinstance(abs_cmd, ClosePath):
            # Close with a line back to start
            if current_pos.x != start_pos.x or current_pos.y != start_pos.y:
                c1x = current_pos.x + (start_pos.x - current_pos.x) / 3
                c1y = current_pos.y + (start_pos.y - current_pos.y) / 3
                c2x = current_pos.x + 2 * (start_pos.x - current_pos.x) / 3
                c2y = current_pos.y + 2 * (start_pos.y - current_pos.y) / 3

                data.extend([c1x, c1y, c2x, c2y, start_pos.x, start_pos.y])
            current_pos = start_pos

    return PolyBezier(data)


# ============================================================================
# Path Normalization (Polymorph Style)
# ============================================================================


def normalize_poly_bezier_start(
    poly: PolyBezier, origin: Point = Point(0, 0)
) -> PolyBezier:
    """
    Normalize poly-bezier to start from the point closest to origin

    This is Polymorph's key optimization - it rotates the path data
    so that morphing starts from corresponding points on both shapes.
    """

    curves = poly.get_curves()
    if len(curves) <= 1:
        return poly  # Nothing to optimize

    # Find the curve whose end point is closest to origin
    min_distance = float("inf")
    best_index = 0

    for i, (start, c1, c2, end) in enumerate(curves):
        dist = end.distance_to(origin)
        if dist < min_distance:
            min_distance = dist
            best_index = i

    if best_index == 0:
        return poly  # Already optimal

    # Rotate the curve data to start from the best position
    # This involves reconstructing the data array with a new starting point
    new_data = []

    # New starting point is the end of the best curve
    best_end = curves[best_index][3]
    new_data.extend([best_end.x, best_end.y])

    # Add curves starting from best_index + 1
    for i in range(best_index + 1, len(curves)):
        start, c1, c2, end = curves[i]
        new_data.extend([c1.x, c1.y, c2.x, c2.y, end.x, end.y])

    # Add curves from 0 to best_index
    for i in range(best_index + 1):
        start, c1, c2, end = curves[i]
        new_data.extend([c1.x, c1.y, c2.x, c2.y, end.x, end.y])

    return PolyBezier(new_data)


# ============================================================================
# Point Filling (Polymorph Style)
# ============================================================================


def fill_poly_bezier_to_length(poly: PolyBezier, target_length: int) -> PolyBezier:
    """
    Fill poly-bezier with duplicate points to reach target length

    Polymorph's approach: instead of subdividing curves geometrically,
    just duplicate the last point of curves to pad the length.
    This preserves the shape while making interpolation possible.
    """

    current_length = len(poly.data)

    if current_length >= target_length:
        return poly

    if current_length < 2:
        # Can't fill an empty path
        return poly

    # Calculate how many points to add
    points_to_add = target_length - current_length

    # Must add in multiples of 6 (cubic curve = 6 values)
    curves_to_add = (points_to_add + 5) // 6
    actual_points_to_add = curves_to_add * 6

    new_data = poly.data.copy()

    # Get the last point of the path
    if len(poly.data) >= 8:  # Has at least one curve
        last_x = poly.data[-2]
        last_y = poly.data[-1]
    else:
        last_x = poly.data[0]
        last_y = poly.data[1]

    # Add duplicate curves (point curves where all control points = end point)
    for _ in range(curves_to_add):
        new_data.extend([last_x, last_y, last_x, last_y, last_x, last_y])

    return PolyBezier(new_data)


# ============================================================================
# Matrix Interpolation (Polymorph Style)
# ============================================================================


def interpolate_poly_beziers(
    poly1: PolyBezier, poly2: PolyBezier, t: float
) -> PolyBezier:
    """
    Interpolate between two poly-beziers using matrix approach

    This is the core of Polymorph's smooth morphing:
    result[i] = poly1[i] + (poly2[i] - poly1[i]) * t

    Simple, elegant, and mathematically sound.
    """

    # Ensure both have the same length
    max_length = max(len(poly1.data), len(poly2.data))

    filled_poly1 = fill_poly_bezier_to_length(poly1, max_length)
    filled_poly2 = fill_poly_bezier_to_length(poly2, max_length)

    # Linear interpolation of all values
    result_data = []
    for i in range(max_length):
        val1 = filled_poly1.data[i] if i < len(filled_poly1.data) else 0
        val2 = filled_poly2.data[i] if i < len(filled_poly2.data) else 0
        result_data.append(val1 + (val2 - val1) * t)

    return PolyBezier(result_data)


# ============================================================================
# Main Polymorph-Style Interface
# ============================================================================


def polymorph_interpolate(
    path1: SVGPath, path2: SVGPath, t: float, origin: Point = Point(0, 0)
) -> SVGPath:
    """
    Polymorph-style path interpolation

    This implements the complete Polymorph algorithm:
    1. Convert paths to poly-bezier format
    2. Normalize starting points
    3. Interpolate using matrix approach
    4. Convert back to SVGPath

    Args:
        path1: First path
        path2: Second path
        t: Interpolation parameter (0.0 to 1.0)
        origin: Origin point for normalization

    Returns:
        Interpolated SVGPath
    """

    # Step 1: Convert to poly-bezier format
    poly1 = convert_to_poly_bezier(path1)
    poly2 = convert_to_poly_bezier(path2)

    # Step 2: Normalize starting points for better correspondence
    normalized_poly1 = normalize_poly_bezier_start(poly1, origin)
    normalized_poly2 = normalize_poly_bezier_start(poly2, origin)

    # Step 3: Interpolate using matrix approach
    result_poly = interpolate_poly_beziers(normalized_poly1, normalized_poly2, t)

    # Step 4: Convert back to SVGPath
    return result_poly.to_svg_path()


# ============================================================================
# Convenience Functions
# ============================================================================


def analyze_poly_bezier_compatibility(path1: SVGPath, path2: SVGPath) -> dict:
    """Analyze how well two paths will morph using polymorph approach"""

    poly1 = convert_to_poly_bezier(path1)
    poly2 = convert_to_poly_bezier(path2)

    curve_count1 = poly1.get_curve_count()
    curve_count2 = poly2.get_curve_count()

    # Calculate complexity ratio
    if curve_count2 == 0:
        complexity_ratio = float("inf") if curve_count1 > 0 else 1.0
    else:
        complexity_ratio = curve_count1 / curve_count2

    # Assess compatibility
    if abs(complexity_ratio - 1.0) < 0.5:
        compatibility = "excellent"
        score = 95
    elif abs(complexity_ratio - 1.0) < 1.0:
        compatibility = "good"
        score = 80
    elif abs(complexity_ratio - 1.0) < 2.0:
        compatibility = "fair"
        score = 60
    else:
        compatibility = "poor"
        score = 30

    return {
        "curve_count1": curve_count1,
        "curve_count2": curve_count2,
        "complexity_ratio": complexity_ratio,
        "compatibility": compatibility,
        "score": score,
        "recommended": score >= 70,
    }
