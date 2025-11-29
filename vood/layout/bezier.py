"""Bezier/path layout state function"""

import math
from typing import Optional, Callable, Sequence
from dataclasses import replace
from vood.component.state.base import States
from .enums import ElementAlignment
from vood.core.point2d import Point2D, Points2D

def bezier(
    states: States,
    control_points: Points2D,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
    arc_length_spacing: bool = True,  # New parameter
) -> States:
    """
    Arrange states along a Bezier curve (quadratic or cubic).

    Args:
        states: List of states to arrange
        control_points: List of (x, y) tuples for Bezier control points (2, 3, or 4 points)
        alignment: How to align each element relative to the curve.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        element_rotation_offset_fn: Function that takes position t (0-1) and returns rotation offset.
        arc_length_spacing: If True, space elements evenly by arc length. If False, use even t spacing.

    Returns:
        New list of states with positions along the Bezier curve
    """

    if not states or not control_points:
        return []
    
    if not isinstance(control_points[0], Point2D):
        raise Exception("bezier control_points must be a list of Point2D objects")

    def bezier_point(t, pts:Points2D) -> Point2D:

        n = len(pts) - 1
        x = sum(
            math.comb(n, i) * (1 - t) ** (n - i) * t**i * pts[i].x
            for i in range(n + 1)
        )
        y = sum(
            math.comb(n, i) * (1 - t) ** (n - i) * t**i * pts[i].y
            for i in range(n + 1)
        )
        return Point2D(x, y)

    def bezier_tangent_angle(t, pts:Points2D) -> float:
        n = len(pts) - 1
        if n == 0:
            return 0

        # Calculate derivative (tangent vector)
        dx = sum(
            n
            * math.comb(n - 1, i)
            * (1 - t) ** (n - 1 - i)
            * t**i
            * (pts[i + 1].x - pts[i].x)
            for i in range(n)
        )
        dy = sum(
            n
            * math.comb(n - 1, i)
            * (1 - t) ** (n - 1 - i)
            * t**i
            * (pts[i + 1].y - pts[i].y)
            for i in range(n)
        )

        # Handle edge case where derivative is zero
        if dx == 0 and dy == 0:
            dt = 1e-5
            if t < 1 - dt:
                p1 = bezier_point(t, pts)
                p2 = bezier_point(t + dt, pts)
            else:
                p1 = bezier_point(t - dt, pts)
                p2 = bezier_point(t, pts)
            dx, dy = p2.x - p1.x, p2.y - p1.y

        angle = math.degrees(math.atan2(dy, dx))
        return angle

    def build_arc_length_table(pts:Points2D, samples=1000) -> tuple[list[float], list[float], float]:
        """Build a lookup table mapping arc length to t parameter"""
        arc_lengths = [0]
        t_values = [0]


        prev_point = bezier_point(0, pts)
        total_length = 0

        for i in range(1, samples + 1):
            t = i / samples
            current_point = bezier_point(t, pts)
            dx = current_point.x - prev_point.x
            dy = current_point.y - prev_point.y
            segment_length = math.sqrt(dx * dx + dy * dy)
            total_length += segment_length

            arc_lengths.append(total_length)
            t_values.append(t)
            prev_point = current_point

        return arc_lengths, t_values, total_length

    def t_from_arc_length(target_length, arc_lengths, t_values):
        """Find t parameter for a given arc length using linear interpolation"""
        if target_length <= 0:
            return 0
        if target_length >= arc_lengths[-1]:
            return 1

        # Binary search for the right segment
        left, right = 0, len(arc_lengths) - 1
        while right - left > 1:
            mid = (left + right) // 2
            if arc_lengths[mid] < target_length:
                left = mid
            else:
                right = mid

        # Linear interpolation
        length_range = arc_lengths[right] - arc_lengths[left]
        if length_range == 0:
            return t_values[left]

        ratio = (target_length - arc_lengths[left]) / length_range
        return t_values[left] + ratio * (t_values[right] - t_values[left])

    # Build arc length table if needed
    if arc_length_spacing:
        arc_lengths, t_values, total_length = build_arc_length_table(control_points)

    num_elements = len(states)
    result = []

    for i, state in enumerate(states):
        if arc_length_spacing and num_elements > 1:
            # Space evenly by arc length
            target_length = (i / (num_elements - 1)) * total_length
            t = t_from_arc_length(target_length, arc_lengths, t_values)
        else:
            # Space evenly by t parameter
            t = i / (num_elements - 1) if num_elements > 1 else 0

        x, y = bezier_point(t, control_points)
        tangent_angle = bezier_tangent_angle(t, control_points)

        additional_rotation = (
            element_rotation_offset_fn(t)
            if element_rotation_offset_fn
            else element_rotation_offset
        )

        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            element_angle = tangent_angle + additional_rotation
        elif alignment == ElementAlignment.UPRIGHT:
            element_angle = additional_rotation
        else:
            element_angle = state.rotation

        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result
