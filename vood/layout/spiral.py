"""Spiral layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace
from vood.component import State
from .enums import ElementAlignment


def spiral(
    states: List[State],
    center_x: float = 0,
    center_y: float = 0,
    start_radius: float = 20,
    radius_step: float = 20,
    start_angle: float = 0,
    angle_step: float = 30,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> List[State]:
    """
    Arrange states in a spiral formation (Archimedean spiral).

    Each element is placed at increasing radius and angle from the center.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        center_x: X coordinate of spiral center
        center_y: Y coordinate of spiral center
        start_radius: Initial radius from center for first element
        radius_step: Amount to increase radius for each subsequent element
        start_angle: Initial angle in degrees for first element
        angle_step: Amount to increase angle for each subsequent element (degrees)
        alignment: How to align each element relative to the spiral.
                  PRESERVE keeps original rotation, LAYOUT aligns tangent to spiral,
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        element_rotation_offset_fn: Function that takes position angle (degrees) and returns rotation offset.
                           If provided, this overrides element_rotation_offset parameter.

    Returns:
        New list of states with spiral positions
    """
    if not states:
        return []

    result = []
    for i, state in enumerate(states):
        radius = start_radius + i * radius_step
        angle = start_angle + i * angle_step
        angle_rad = math.radians(angle)

        # Calculate position (y is flipped for SVG)
        x = center_x + radius * math.sin(angle_rad)
        y = center_y - radius * math.cos(angle_rad)

        additional_rotation = (
            element_rotation_offset_fn(angle)
            if element_rotation_offset_fn
            else element_rotation_offset
        )

        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            # upright to the center
            element_angle = angle + additional_rotation
        elif alignment == ElementAlignment.UPRIGHT:
            element_angle = additional_rotation
        else:
            element_angle = state.rotation

        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result
