"""Circle layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace

from vood.component import State
from .enums import ElementAlignment


def circle(
    states: List[State],
    radius: float = 100,
    rotation: float = 0,
    center_x: float = 0,
    center_y: float = 0,
    clockwise: bool = True,
    angles: Optional[List[float]] = None,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
    radius_fn: Optional[Callable[[int, float], float]] = None,
) -> List[State]:

    if not states:
        return []

    result = []

    # Use custom angles if provided, otherwise calculate even distribution
    if angles is not None:
        if len(angles) < len(states):
            raise ValueError(
                f"Length of angles ({len(angles)}) must be equal or bigger than length of states ({len(states)})"
            )
        element_angles = angles
    else:
        # Calculate even distribution
        num_elements = len(states)
        angle_step = 360 / num_elements
        element_angles = [
            i * angle_step if clockwise else -i * angle_step
            for i in range(num_elements)
        ]

    # Position each element at its calculated angle
    for i, state in enumerate(states):
        angle = rotation + element_angles[i]

        # Convert to radians for math functions
        angle_rad = math.radians(angle)

        # Calculate radius for this element
        r = radius_fn(i, radius) if radius_fn else radius

        # Calculate position (note: y is flipped because SVG y increases downward)
        x = center_x + r * math.sin(angle_rad)
        y = center_y - r * math.cos(angle_rad)

        # Calculate additional rotation (function-based or static)
        additional_rotation = (
            element_rotation_offset_fn(angle)
            if element_rotation_offset_fn
            else element_rotation_offset
        )

        # Calculate element rotation based on alignment mode
        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            # Align with layout direction (tangent to circle) + additional rotation
            element_angle = angle + additional_rotation
        elif alignment == ElementAlignment.UPRIGHT:
            # Start from upright position + additional rotation
            element_angle = additional_rotation
        else:
            element_angle = state.rotation

        # Create new state with circular position and rotation, preserving all other properties
        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result
