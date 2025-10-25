"""Circle layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace

from vood.components import State
from .enums import ElementAlignment


def circle_layout(
    states: List[State],
    radius: float = 100,
    rotation: float = 0,
    center_x: float = 0,
    center_y: float = 0,
    clockwise: bool = True,
    angles: Optional[List[float]] = None,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation: float = 0,
    element_rotation_fn: Optional[Callable[[float], float]] = None,
    radius_fn: Optional[Callable[[int, float], float]] = None,
) -> List[State]:
    """
    Arrange states in a circular formation.

    Positions elements around a circle, either evenly distributed or at specific angles.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        radius: Distance from center to each element
        rotation: Rotation in degrees (0° = top, 90° = right).
        center_x: X coordinate of circle center
        center_y: Y coordinate of circle center
        clockwise: If True, arrange clockwise; if False, counterclockwise.
                  Only used when angles is None.
        angles: Optional list of specific angles in degrees for each element.
               If provided, overrides automatic distribution and clockwise parameter.
               List length should match states length.
        alignment: How to align each element relative to the circle.
                  PRESERVE keeps original rotation, LAYOUT aligns tangent to circle,
                  UPRIGHT starts from vertical position.
        element_rotation: Additional rotation in degrees added to the alignment base.
        element_rotation_fn: Function that takes position angle (degrees) and returns rotation offset.
                           If provided, this overrides element_rotation parameter.

    Returns:
        New list of states with circular positions

    Examples:
        # Even distribution (full circle)
        >>> states = [CircleState(), CircleState(), CircleState()]
        >>> circle_layout(states, radius=100)

        # Half circle arrangement
        >>> half_circle = circle_layout(states, angles=[180, 225, 270])

        # Custom angles for specific positioning
        >>> custom = circle_layout(states, angles=[0, 45, 180])

        # Position-aware rotation (elements lean inward)
        >>> def lean_inward(angle):
        ...     if 270 <= angle <= 360 or 0 <= angle < 90:  # Right side
        ...         return -90
        ...     else:  # Left side
        ...         return 90
        >>> leaning = circle_layout(states, element_rotation_fn=lean_inward)
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
        # Calculate even distribution
        num_elements = len(states)
        angle_step = 360 / num_elements
        element_angles = []
        for i in range(num_elements):
            angle = i * angle_step if clockwise else -i * angle_step
            element_angles.append(angle)

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
            element_rotation_fn(angle) if element_rotation_fn else element_rotation
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
