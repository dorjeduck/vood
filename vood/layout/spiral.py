"""Spiral layout state function"""

import math
from typing import Optional, Callable
from dataclasses import replace
from vood.component.state.base import States

from .enums import ElementAlignment


def spiral(
    states: States,
    cx: float = 0,
    cy: float = 0,
    start_radius: float = 20,
    radius_step: float = 20,
    start_angle: float = 0,
    angle_step: float = 30,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> States:
    """
    Arrange states in a spiral formation (Archimedean spiral).

    Each element is placed at increasing radius and angle from the center.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        cx: X coordinate of spiral center
        cy: Y coordinate of spiral center
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
        x = cx + radius * math.sin(angle_rad)
        y = cy - radius * math.cos(angle_rad)

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


def spiral_between_radii(
    states: States,
    cx: float = 0,
    cy: float = 0,
    start_radius: float = 50,
    end_radius: float = 200,
    rotation: float = 0,
    clockwise: bool = False,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> States:
    """
    Arrange states in a spiral from start radius to end radius.

    Alternative specification to spiral() for users who think in terms of target
    end radius rather than radius step. The spiral will grow/shrink to reach
    the specified end radius.

    Args:
        states: List of states to arrange
        cx: X coordinate of spiral center
        cy: Y coordinate of spiral center
        start_radius: Radius for first element
        end_radius: Radius for last element
        rotation: Base rotation offset in degrees
        clockwise: If True, spiral clockwise; if False, counterclockwise
        alignment: How to align each element
        element_rotation_offset: Additional rotation offset
        element_rotation_offset_fn: Function(angle) -> rotation offset

    Returns:
        New list of states with spiral positions

    Examples:
        # Spiral outward from 50 to 200
        >>> spiral_between_radii(states, start_radius=50, end_radius=200)

        # Spiral inward (negative step)
        >>> spiral_between_radii(states, start_radius=200, end_radius=50)

        # Equivalent to spiral():
        # spiral_between_radii(states, start_radius=50, end_radius=200) with 5 states
        # == spiral(states, start_radius=50, radius_step=37.5) with 5 states
    """
    if not states:
        return []

    num_elements = len(states)

    # Calculate radius step to reach end_radius
    # For n elements: radius[i] = start_radius + i * radius_step
    # We want radius[n-1] = end_radius
    radius_step = (
        (end_radius - start_radius) / (num_elements - 1) if num_elements > 1 else 0
    )

    # Calculate angle step based on direction
    # Use 30 degrees as default (same as spiral default)
    angle_step = 30 if not clockwise else -30

    # Call canonical spiral function
    return spiral(
        states,
        cx=cx,
        cy=cy,
        start_radius=start_radius,
        radius_step=radius_step,
        start_angle=rotation,
        angle_step=angle_step,
        alignment=alignment,
        element_rotation_offset=element_rotation_offset,
        element_rotation_offset_fn=element_rotation_offset_fn,
    )
