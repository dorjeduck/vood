# ============================================================================
# vood/paths/subdivision.py
# ============================================================================
"""
Robust path subdivision for morphing

Implements proper curve subdivision with full tracking of:
- Current position throughout path
- Start position for ClosePath commands
- Proper absolute/relative coordinate handling
"""

from __future__ import annotations
from typing import Tuple, List
from dataclasses import dataclass

from vood.path.commands import (
    PathCommand,
    MoveTo,
    LineTo,
    QuadraticBezier,
    CubicBezier,
    ClosePath,
)
from vood.core.point2d import Point2D


@dataclass
class PathContext:
    """Tracks state while traversing a path"""

    current_pos: Point2D
    last_move_pos: Point2D  # For ClosePath

    @classmethod
    def initial(cls) -> PathContext:
        """Create initial context at origin"""
        origin = Point2D(0.0, 0.0)
        return cls(current_pos=origin, last_move_pos=origin)


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation"""
    return a + (b - a) * t


def lerp_point(p1: Point2D, p2: Point2D, t: float) -> Point2D:
    """Linear interpolation between two points"""
    return Point2D(x=lerp(p1.x, p2.x, t), y=lerp(p1.y, p2.y, t))


# ============================================================================
# Curve Subdivision Functions
# ============================================================================


def subdivide_line(
    start: Point2D, end: Point2D, t: float = 0.5
) -> Tuple[Point2D, Point2D, Point2D]:
    """Subdivide a line segment at parameter t

    Args:
        start: Start point
        end: End point
        t: Parameter at which to split (0.0 to 1.0)

    Returns:
        Tuple of (midpoint, end_of_first, start_of_second)
        For lines, end_of_first == start_of_second == midpoint
    """
    mid = lerp_point(start, end, t)
    return mid, mid, mid


def subdivide_quadratic(
    start: Point2D, control: Point2D, end: Point2D, t: float = 0.5
) -> Tuple[Point2D, Point2D, Point2D, Point2D, Point2D]:
    """Subdivide a quadratic Bezier curve at parameter t

    Uses De Casteljau's algorithm.

    Args:
        start: Start point (P0)
        control: Control point (P1)
        end: End point (P2)
        t: Parameter at which to split (0.0 to 1.0)

    Returns:
        Tuple of (split_point, c1_first, c1_second, end_first, start_second)
        - split_point: Point where curves meet
        - c1_first: Control point for first curve
        - c1_second: Control point for second curve
    """
    # First level of interpolation
    q0 = lerp_point(start, control, t)
    q1 = lerp_point(control, end, t)

    # Second level - this is the split point
    split_point = lerp_point(q0, q1, t)

    return split_point, q0, q1, split_point, split_point


def subdivide_cubic(
    start:  Point2D,
    control1: Point2D,
    control2: Point2D,
    end: Point2D,
    t: float = 0.5,
) -> Tuple[Point2D, Point2D, Point2D, Point2D, Point2D]:
    """Subdivide a cubic Bezier curve at parameter t

    Uses De Casteljau's algorithm.

    Args:
        start: Start point (P0)
        control1: First control point (P1)
        control2: Second control point (P2)
        end: End point (P3)
        t: Parameter at which to split (0.0 to 1.0)

    Returns:
        Tuple of (split_point, c1_first, c2_first, c1_second, c2_second)
        - split_point: Point where curves meet
        - c1_first, c2_first: Control points for first curve
        - c1_second, c2_second: Control points for second curve
    """
    # First level of interpolation
    q0 = lerp_point(start, control1, t)
    q1 = lerp_point(control1, control2, t)
    q2 = lerp_point(control2, end, t)

    # Second level
    r0 = lerp_point(q0, q1, t)
    r1 = lerp_point(q1, q2, t)

    # Third level - this is the split point
    split_point = lerp_point(r0, r1, t)

    return split_point, q0, r0, r1, q2


# ============================================================================
# Command Subdivision
# ============================================================================


def subdivide_command(
    cmd: PathCommand, context: PathContext, t: float = 0.5
) -> Tuple[List[PathCommand], PathContext]:
    """Subdivide a single path command at parameter t

    Args:
        cmd: Command to subdivide
        context: Current path context
        t: Parameter at which to split

    Returns:
        Tuple of (new_commands, new_context)
        new_commands will have 2 commands for curves, 1 for non-subdivided
    """
    # Convert to absolute if needed
    abs_cmd = cmd.to_absolute(context.current_pos.as_tuple())

    if isinstance(abs_cmd, MoveTo):
        # MoveTo doesn't subdivide, just updates context
        new_pos = Point2D(abs_cmd.x, abs_cmd.y)
        new_context = PathContext(current_pos=new_pos, last_move_pos=new_pos)
        return [abs_cmd], new_context

    elif isinstance(abs_cmd, LineTo):
        # Convert line to cubic Bezier, then subdivide
        start = context.current_pos
        end = Point2D(abs_cmd.x, abs_cmd.y)

        # Line as cubic: control points at 1/3 and 2/3
        c1 = lerp_point(start, end, 1 / 3)
        c2 = lerp_point(start, end, 2 / 3)

        # Subdivide the cubic
        split, q0, r0, r1, q2 = subdivide_cubic(start, c1, c2, end, t)

        # Create two cubic Bezier commands
        first = CubicBezier(q0.x, q0.y, r0.x, r0.y, split.x, split.y, absolute=True)
        second = CubicBezier(r1.x, r1.y, q2.x, q2.y, end.x, end.y, absolute=True)

        new_context = PathContext(current_pos=end, last_move_pos=context.last_move_pos)
        return [first, second], new_context

    elif isinstance(abs_cmd, QuadraticBezier):
        # Convert quadratic to cubic, then subdivide
        start = context.current_pos
        qc = Point2D(abs_cmd.cx, abs_cmd.cy)
        end = Point2D(abs_cmd.x, abs_cmd.y)

        # Quadratic to cubic conversion
        c1 = Point2D(
            start.x + 2 / 3 * (qc.x - start.x), start.y + 2 / 3 * (qc.y - start.y)
        )
        c2 = Point2D(end.x + 2 / 3 * (qc.x - end.x), end.y + 2 / 3 * (qc.y - end.y))

        # Subdivide the cubic
        split, q0, r0, r1, q2 = subdivide_cubic(start, c1, c2, end, t)

        # Create two cubic Bezier commands
        first = CubicBezier(q0.x, q0.y, r0.x, r0.y, split.x, split.y, absolute=True)
        second = CubicBezier(r1.x, r1.y, q2.x, q2.y, end.x, end.y, absolute=True)

        new_context = PathContext(current_pos=end, last_move_pos=context.last_move_pos)
        return [first, second], new_context

    elif isinstance(abs_cmd, CubicBezier):
        # Subdivide cubic directly
        start = context.current_pos
        c1 = Point2D(abs_cmd.cx1, abs_cmd.cy1)
        c2 = Point2D(abs_cmd.cx2, abs_cmd.cy2)
        end = Point2D(abs_cmd.x, abs_cmd.y)

        # Subdivide
        split, q0, r0, r1, q2 = subdivide_cubic(start, c1, c2, end, t)

        # Create two cubic Bezier commands
        first = CubicBezier(q0.x, q0.y, r0.x, r0.y, split.x, split.y, absolute=True)
        second = CubicBezier(r1.x, r1.y, q2.x, q2.y, end.x, end.y, absolute=True)

        new_context = PathContext(current_pos=end, last_move_pos=context.last_move_pos)
        return [first, second], new_context

    elif isinstance(abs_cmd, ClosePath):
        # ClosePath doesn't subdivide
        new_context = PathContext(
            current_pos=context.last_move_pos,  # Returns to last MoveTo
            last_move_pos=context.last_move_pos,
        )
        return [abs_cmd], new_context

    else:
        # Unknown command - don't subdivide
        end_pos = abs_cmd.get_end_point(context.current_pos.as_tuple())
        new_context = PathContext(
            current_pos=Point2D(*end_pos), last_move_pos=context.last_move_pos
        )
        return [abs_cmd], new_context


# ============================================================================
# Curve Length Estimation
# ============================================================================


def estimate_cubic_length(
    start: Point2D,
    c1: Point2D,
    c2: Point2D,
    end: Point2D,
    num_samples: int = 10,
) -> float:
    """Estimate the length of a cubic Bezier curve

    Uses linear approximation with multiple samples.

    Args:
        start, c1, c2, end: Control points
        num_samples: Number of samples for approximation

    Returns:
        Approximate length of curve
    """

    def cubic_point(t: float) -> Point2D:
        """Evaluate cubic Bezier at parameter t"""
        t2 = t * t
        t3 = t2 * t
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt

        return Point2D(
            x=mt3 * start.x + 3 * mt2 * t * c1.x + 3 * mt * t2 * c2.x + t3 * end.x,
            y=mt3 * start.y + 3 * mt2 * t * c1.y + 3 * mt * t2 * c2.y + t3 * end.y,
        )

    length = 0.0
    prev_point = start

    for i in range(1, num_samples + 1):
        t = i / num_samples
        point = cubic_point(t)
        length += prev_point.distance_to(point)
        prev_point = point

    return length


def estimate_command_length(cmd: PathCommand, context: PathContext) -> float:
    """Estimate the visual length of a path command

    Args:
        cmd: Command to measure
        context: Current path context

    Returns:
        Approximate length
    """
    abs_cmd = cmd.to_absolute(context.current_pos.as_tuple())

    if isinstance(abs_cmd, (MoveTo, ClosePath)):
        return 0.0

    elif isinstance(abs_cmd, LineTo):
        start = context.current_pos
        end = Point2D(abs_cmd.x, abs_cmd.y)
        return start.distance_to(end)

    elif isinstance(abs_cmd, QuadraticBezier):
        # Convert to cubic and measure
        start = context.current_pos
        qc = Point2D(abs_cmd.cx, abs_cmd.cy)
        end = Point2D(abs_cmd.x, abs_cmd.y)

        c1 = Point2D(
            start.x + 2 / 3 * (qc.x - start.x), start.y + 2 / 3 * (qc.y - start.y)
        )
        c2 = Point2D(end.x + 2 / 3 * (qc.x - end.x), end.y + 2 / 3 * (qc.y - end.y))

        return estimate_cubic_length(start, c1, c2, end)

    elif isinstance(abs_cmd, CubicBezier):
        start = context.current_pos
        c1 = Point2D(abs_cmd.cx1, abs_cmd.cy1)
        c2 = Point2D(abs_cmd.cx2, abs_cmd.cy2)
        end = Point2D(abs_cmd.x, abs_cmd.y)

        return estimate_cubic_length(start, c1, c2, end)

    else:
        # Fallback: straight line distance
        start = context.current_pos
        end_tuple = abs_cmd.get_end_point(start.as_tuple())
        end = Point2D(*end_tuple)
        return start.distance_to(end)


# ============================================================================
# Path Analysis
# ============================================================================


@dataclass
class CurveInfo:
    """Information about a curve segment in a path"""

    index: int  # Index in commands list
    command: PathCommand
    length: float
    start_context: PathContext


def analyze_path_curves(commands: List[PathCommand]) -> List[CurveInfo]:
    """Analyze all curves in a path

    Args:
        commands: List of path commands

    Returns:
        List of CurveInfo for all drawable curves (excludes MoveTo, ClosePath)
    """
    curves = []
    context = PathContext.initial()

    for i, cmd in enumerate(commands):
        # Skip non-drawable commands
        if isinstance(cmd, (MoveTo, ClosePath)):
            # Update context but don't add to curves
            abs_cmd = cmd.to_absolute(context.current_pos.as_tuple())
            end_pos = abs_cmd.get_end_point(context.current_pos.as_tuple())

            if isinstance(cmd, MoveTo):
                new_pos = Point2D(*end_pos)
                context = PathContext(current_pos=new_pos, last_move_pos=new_pos)
            else:  # ClosePath
                context = PathContext(
                    current_pos=context.last_move_pos,
                    last_move_pos=context.last_move_pos,
                )
            continue

        # Measure curve length
        length = estimate_command_length(cmd, context)

        # Store curve info
        curves.append(
            CurveInfo(index=i, command=cmd, length=length, start_context=context)
        )

        # Update context
        abs_cmd = cmd.to_absolute(context.current_pos.as_tuple())
        end_pos = abs_cmd.get_end_point(context.current_pos.as_tuple())
        context = PathContext(
            current_pos=Point2D(*end_pos), last_move_pos=context.last_move_pos
        )

    return curves


# ============================================================================
# Smart Subdivision
# ============================================================================


def subdivide_path_to_count(
    commands: List[PathCommand], target_curve_count: int
) -> List[PathCommand]:
    """Subdivide curves in a path until reaching target count

    Strategy: Repeatedly subdivide the longest curve for even distribution.

    Args:
        commands: Original path commands
        target_curve_count: Desired number of curve segments

    Returns:
        New list of commands with subdivided curves
    """
    if target_curve_count <= 0:
        return commands

    # Analyze current curves
    curves = analyze_path_curves(commands)
    current_count = len(curves)

    if current_count >= target_curve_count:
        return commands

    # Work with a copy
    result = list(commands)

    # Keep subdividing until we reach target
    while current_count < target_curve_count:
        # Re-analyze after each subdivision
        curves = analyze_path_curves(result)

        if not curves:
            break

        # Find longest curve
        longest = max(curves, key=lambda c: c.length)

        # Subdivide it
        subdivided, new_context = subdivide_command(
            longest.command, longest.start_context, t=0.5
        )

        # Replace in result
        # Need to find actual position (might have shifted due to previous subdivisions)
        # For now, we'll rebuild from scratch each time
        result = _rebuild_with_subdivision(result, longest.index, subdivided)

        # Re-analyze to get actual curve count
        new_curves = analyze_path_curves(result)
        actual_curve_count = len(new_curves)
        current_count = actual_curve_count  # Use actual count, not increment

    return result


def _rebuild_with_subdivision(
    commands: List[PathCommand], command_index: int, new_commands: List[PathCommand]
) -> List[PathCommand]:
    """Rebuild command list with a subdivided curve

    Args:
        commands: Original commands
        command_index: Index of command to replace (in original list)
        new_commands: Subdivision result (usually 2 commands)

    Returns:
        New command list
    """
    # Replace the command at command_index with new_commands
    result = []

    for i, cmd in enumerate(commands):
        if i == command_index:
            # Replace with subdivided version
            result.extend(new_commands)
        else:
            result.append(cmd)

    return result
