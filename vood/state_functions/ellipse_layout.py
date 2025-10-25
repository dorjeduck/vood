"""Ellipse layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace

from vood.components import State
from .enums import ElementAlignment


def ellipse_layout(
    states: List[State],
    radius_x: float = 100,
    radius_y: float = 50,
    rotation: float = 0,
    center_x: float = 0,
    center_y: float = 0,
    clockwise: bool = True,
    start_angle: float = 0,
    angles: Optional[List[float]] = None,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation: float = 0,
    element_rotation_fn: Optional[Callable[[float], float]] = None,
) -> List[State]:
    """
    Arrange states in an elliptical formation.

    Positions elements around an ellipse, either evenly distributed or at specific angles.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        radius_x: Horizontal radius of the ellipse
        radius_y: Vertical radius of the ellipse
        rotation: Rotation in degrees (0° = top, 90° = right)
        center_x: X coordinate of ellipse center
        center_y: Y coordinate of ellipse center
        clockwise: If True, arrange clockwise; if False, counterclockwise.
                  Only used when angles is None.
        angles: Optional list of specific angles in degrees for each element.
               If provided, overrides automatic distribution and clockwise parameter.
               List length should match states length.
        alignment: How to align each element relative to the ellipse.
                  PRESERVE keeps original rotation, LAYOUT aligns tangent to ellipse,
                  UPRIGHT starts from vertical position.
        element_rotation: Additional rotation in degrees added to the alignment base.
        element_rotation_fn: Function that takes position angle (degrees) and returns rotation offset.
                           If provided, this overrides element_rotation parameter.

    Returns:
        New list of states with elliptical positions
    """
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
        num_elements = len(states)
        angle_step = 360 / num_elements
        if clockwise:
            element_angles = [start_angle + i * angle_step for i in range(num_elements)]
        else:
            element_angles = [
                start_angle + 360 - i * angle_step for i in range(num_elements)
            ]

    rot_rad = math.radians(rotation)
    cos_rot = math.cos(rot_rad)
    sin_rot = math.sin(rot_rad)

    for i, state in enumerate(states):
        angle = element_angles[i]
        angle_rad = math.radians(angle)

        # Position on unrotated ellipse
        ex = radius_x * math.sin(angle_rad)
        ey = -radius_y * math.cos(angle_rad)

        # Rotate ellipse axes by 'rotation'
        x = center_x + ex * cos_rot - ey * sin_rot
        y = center_y + ex * sin_rot + ey * cos_rot

        additional_rotation = (
            element_rotation_fn(angle) if element_rotation_fn else element_rotation
        )

        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            # Tangent to ellipse at this angle (approximate by using angle + 90)
            element_angle = angle + 90 + additional_rotation
        elif alignment == ElementAlignment.UPRIGHT:
            element_angle = additional_rotation
        else:
            element_angle = state.rotation

        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result
