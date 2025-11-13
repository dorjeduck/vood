from .commands import (
    MoveTo,
    LineTo,
    QuadraticBezier,
    CubicBezier,
    ClosePath,
)
from .svg_path import SVGPath


# ============================================================================
# Helper functions for creating common paths
# ============================================================================


def line(x1: float, y1: float, x2: float, y2: float) -> SVGPath:
    """Create a straight line path"""
    return SVGPath([MoveTo(x1, y1), LineTo(x2, y2)])


def quadratic_curve(
    x1: float, y1: float, cx: float, cy: float, x2: float, y2: float
) -> SVGPath:
    """Create a quadratic Bezier curve path"""
    return SVGPath([MoveTo(x1, y1), QuadraticBezier(cx, cy, x2, y2)])


def cubic_curve(
    x1: float,
    y1: float,
    cx1: float,
    cy1: float,
    cx2: float,
    cy2: float,
    x2: float,
    y2: float,
) -> SVGPath:
    """Create a cubic Bezier curve path"""
    return SVGPath([MoveTo(x1, y1), CubicBezier(cx1, cy1, cx2, cy2, x2, y2)])


def rectangle(x: float, y: float, width: float, height: float) -> SVGPath:
    """Create a rectangle path"""
    return SVGPath(
        [
            MoveTo(x, y),
            LineTo(x + width, y),
            LineTo(x + width, y + height),
            LineTo(x, y + height),
            ClosePath(),
        ]
    )


def circle_as_beziers(cx: float, cy: float, radius: float) -> SVGPath:
    """Create a circle path using cubic Bezier curves

    Uses the magic constant 0.551915024494 for circle approximation
    """
    k = 0.551915024494  # Magic constant for circle with cubic beziers

    return SVGPath(
        [
            MoveTo(cx, cy - radius),  # Top
            CubicBezier(
                cx + k * radius,
                cy - radius,
                cx + radius,
                cy - k * radius,
                cx + radius,
                cy,
            ),  # Right
            CubicBezier(
                cx + radius,
                cy + k * radius,
                cx + k * radius,
                cy + radius,
                cx,
                cy + radius,
            ),  # Bottom
            CubicBezier(
                cx - k * radius,
                cy + radius,
                cx - radius,
                cy + k * radius,
                cx - radius,
                cy,
            ),  # Left
            CubicBezier(
                cx - radius,
                cy - k * radius,
                cx - k * radius,
                cy - radius,
                cx,
                cy - radius,
            ),  # Back to top
            ClosePath(),
        ]
    )
