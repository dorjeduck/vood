"""Bezier/path layout state function"""

import math
from typing import List, Optional, Callable, Sequence
from dataclasses import replace
from vood.components import State
from .enums import ElementAlignment


def bezier_layout(
    states: List[State],
    control_points: Sequence[tuple],
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation: float = 0,
    element_rotation_fn: Optional[Callable[[float], float]] = None,
) -> List[State]:
    """
    Arrange states along a Bezier curve (quadratic or cubic).

    Positions elements at evenly spaced t values along the curve defined by control_points.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        control_points: List of (x, y) tuples for Bezier control points (2, 3, or 4 points)
        alignment: How to align each element relative to the curve.
                  PRESERVE keeps original rotation, LAYOUT aligns tangent to curve,
                  UPRIGHT starts from vertical position.
        element_rotation: Additional rotation in degrees added to the alignment base.
        element_rotation_fn: Function that takes position t (0-1) and returns rotation offset.
                           If provided, this overrides element_rotation parameter.

    Returns:
        New list of states with positions along the Bezier curve
    """
    if not states or not control_points:
        return []

    def bezier_point(t, pts):
        n = len(pts) - 1
        x = sum(
            math.comb(n, i) * (1 - t) ** (n - i) * t**i * pts[i][0]
            for i in range(n + 1)
        )
        y = sum(
            math.comb(n, i) * (1 - t) ** (n - i) * t**i * pts[i][1]
            for i in range(n + 1)
        )
        return x, y

    def bezier_tangent_angle(t, pts):
        n = len(pts) - 1
        dx = sum(
            math.comb(n, i) * (1 - t) ** (n - i) * t**i * pts[i][0]
            for i in range(n + 1)
        )
        dy = sum(
            math.comb(n, i) * (1 - t) ** (n - i) * t**i * pts[i][1]
            for i in range(n + 1)
        )
        # Approximate tangent by finite difference
        dt = 1e-5
        x1, y1 = bezier_point(t, pts)
        x2, y2 = bezier_point(min(t + dt, 1), pts)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        return angle

    num_elements = len(states)
    result = []
    for i, state in enumerate(states):
        t = i / (num_elements - 1) if num_elements > 1 else 0
        x, y = bezier_point(t, control_points)
        tangent_angle = bezier_tangent_angle(t, control_points)

        additional_rotation = (
            element_rotation_fn(t) if element_rotation_fn else element_rotation
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
