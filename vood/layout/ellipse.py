"""Ellipse layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace

from vood.component.state.base import States

from .enums import ElementAlignment


def ellipse(
    states: States,
    rx: float = 100,
    ry: float = 50,
    rotation: float = 0,
    cx: float = 0,
    cy: float = 0,
    clockwise: bool = True,
    start_angle: float = 0,
    angles: Optional[List[float]] = None,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> States:
    """
    Arrange states in an elliptical formation.

    Positions elements around an ellipse, either evenly distributed or at specific angles.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        rx: Horizontal radius of the ellipse
        ry: Vertical radius of the ellipse
        rotation: Rotation in degrees (0° = top, 90° = right)
        cx: X coordinate of ellipse center
        cy: Y coordinate of ellipse center
        clockwise: If True, arrange clockwise; if False, counterclockwise.
                  Only used when angles is None.
        angles: Optional list of specific angles in degrees for each element.
               If provided, overrides automatic distribution and clockwise parameter.
               List length should match states length.
        alignment: How to align each element relative to the ellipse.
                  PRESERVE keeps original rotation, LAYOUT aligns tangent to ellipse,
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        element_rotation_offset_fn: Function that takes position angle (degrees) and returns rotation offset.
                           If provided, this overrides element_rotation_offset parameter.

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
        ex = rx * math.sin(angle_rad)
        ey = -ry * math.cos(angle_rad)

        # Rotate ellipse axes by 'rotation'
        x = cx + ex * cos_rot - ey * sin_rot
        y = cy + ex * sin_rot + ey * cos_rot

        additional_rotation = (
            element_rotation_offset_fn(angle)
            if element_rotation_offset_fn
            else element_rotation_offset
        )

        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation + additional_rotation
        elif alignment == ElementAlignment.LAYOUT:
            # Tangent to ellipse includes the ellipse's rotation
            element_angle = angle + rotation + additional_rotation
        elif alignment == ElementAlignment.UPRIGHT:
            element_angle = additional_rotation

        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result


def ellipse_in_bbox(
    states: States,
    x: float,
    y: float,
    width: float,
    height: float,
    rotation: float = 0,
    clockwise: bool = True,
    start_angle: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    angles: Optional[List[float]] = None,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> States:
    """
    Arrange states in an elliptical formation within a bounding box.

    Alternative specification to ellipse() for users who think in terms of bounding boxes
    rather than center + radii. The ellipse will be inscribed in the specified rectangle.

    Args:
        states: List of states to arrange
        x: X coordinate of bounding box top-left corner
        y: Y coordinate of bounding box top-left corner
        width: Width of bounding box
        height: Height of bounding box
        rotation: Rotation in degrees (0° = top, 90° = right)
        clockwise: If True, arrange clockwise; if False, counterclockwise
        start_angle: Starting angle in degrees for first element
        alignment: How to align each element relative to the ellipse.
                  PRESERVE keeps original rotation, LAYOUT aligns tangent to ellipse,
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        angles: Optional list of specific angles in degrees for each element.
               If provided, overrides automatic distribution.
        element_rotation_offset_fn: Function that takes position angle (degrees) and returns rotation offset.

    Returns:
        New list of states with elliptical positions

    Raises:
        ValueError: If width or height is zero or negative

    Examples:
        # Ellipse in 400x200 box at origin
        >>> ellipse_in_bbox(states, 0, 0, 400, 200)

        # Ellipse in square box (becomes circle)
        >>> ellipse_in_bbox(states, -100, -100, 200, 200)

        # Rotated ellipse in rectangular box
        >>> ellipse_in_bbox(states, 50, 50, 300, 150, rotation=45)

        # Equivalent to ellipse() with center and radii:
        # ellipse_in_bbox(states, 0, 0, 400, 200)
        # == ellipse(states, cx=200, cy=100, rx=200, ry=100)
    """
    if not states:
        return []

    # Validate dimensions
    if width <= 0:
        raise ValueError(f"Width must be positive, got {width}")
    if height <= 0:
        raise ValueError(f"Height must be positive, got {height}")

    # Convert bounding box to center + radii
    cx = x + width / 2
    cy = y + height / 2
    rx = width / 2
    ry = height / 2

    # Call canonical ellipse function
    return ellipse(
        states,
        rx=rx,
        ry=ry,
        rotation=rotation,
        cx=cx,
        cy=cy,
        clockwise=clockwise,
        start_angle=start_angle,
        angles=angles,
        alignment=alignment,
        element_rotation_offset=element_rotation_offset,
        element_rotation_offset_fn=element_rotation_offset_fn,
    )
