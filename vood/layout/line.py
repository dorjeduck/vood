"""Line layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace

from vood.component.state.base import States
from .enums import ElementAlignment


def line(
    states: States,
    spacing: float = 100,
    rotation: float = 0,
    cx: float = 0,
    cy: float = 0,
    distances: Optional[List[float]] = None,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
) -> States:
    """
    Arrange states in a straight line formation.

    Positions elements along a straight line with configurable spacing, rotation, and center point.
    For odd numbers of elements, one element is placed at the center. For even numbers,
    elements are distributed symmetrically around the center point.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        spacing: Distance between adjacent elements. Only used when distances is None.
        rotation: Angle of the line in degrees (0° = horizontal right, 90° = vertical down)
        cx: X coordinate of line center
        cy: Y coordinate of line center
        distances: Optional list of specific distances from center for each element.
                  If provided, overrides automatic distribution and spacing parameter.
                  Positive values = forward along line, negative = backward along line.
                  List length should match states length.
        alignment: How to align each element relative to the line.
                  PRESERVE keeps original rotation, LAYOUT aligns parallel to line,
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.

    Returns:
        New list of states with line positions

    Examples:
        # Even spacing (automatic distribution)
        >>> line_layout(states, spacing=50, rotation=0)

        # Explicit distances from center
        >>> line_layout(states, distances=[-100, -20, 50, 150])

        # Mixed: some bunched together, others spread out
        >>> line_layout(states, distances=[-50, -45, 0, 100, 200])

        # Elements aligned with line direction
        >>> line_layout(states, rotation=45, element_rotation_offset=ElementRotation.ALIGN)

        # Elements kept upright regardless of line rotation
        >>> line_layout(states, rotation=45, element_rotation_offset=ElementRotation.UPRIGHT)

        # Elements upside down (useful for text hanging from a line)
        >>> line_layout(states, element_rotation_offset=ElementRotation.HEADS_DOWN)

        # Elements aligned opposite to line direction (pointing backward)
        >>> line_layout(states, rotation=45, element_rotation_offset=ElementRotation.ALIGN_REVERSE)
    """
    if not states:
        return []

    result = []

    # Use explicit distances if provided, otherwise calculate even distribution
    if distances is not None:
        if len(distances) < len(states):
            raise ValueError(
                f"Length of distances ({len(distances)}) must be equal or bigger than length of states ({len(states)})"
            )
        line_positions = distances
    else:
        # Calculate automatic distribution
        num_elements = len(states)

        if num_elements % 2 == 1:
            # Odd number of elements - one at center
            center_index = num_elements // 2
            line_positions = [(i - center_index) * spacing for i in range(num_elements)]
        else:
            # Even number of elements - symmetric around center
            line_positions = [
                (i - (num_elements - 1) / 2) * spacing for i in range(num_elements)
            ]

    # Convert line positions to 2D coordinates
    rotation_rad = math.radians(rotation)
    cos_rotation = math.cos(rotation_rad)
    sin_rotation = math.sin(rotation_rad)

    for i, state in enumerate(states):
        line_pos = line_positions[i]

        # Calculate position along the line
        x = cx + line_pos * cos_rotation
        y = cy + line_pos * sin_rotation

        # Calculate element rotation based on alignment mode
        if alignment == ElementAlignment.PRESERVE:
            element_rot = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            # Align with line direction + additional rotation
            element_rot = rotation + element_rotation_offset
        elif alignment == ElementAlignment.UPRIGHT:
            # Start from upright position + additional rotation
            element_rot = element_rotation_offset
        else:
            element_rot = state.rotation

        # Create new state with line position and rotation
        new_state = replace(state, x=x, y=y, rotation=element_rot)
        result.append(new_state)

    return result


def line_between_points(
    states: States,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    distances: Optional[List[float]] = None,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> States:
    """
    Arrange states along a line from point A to point B.

    Alternative specification to line() for users who think in terms of endpoints
    rather than center + rotation + spacing. Distributes states evenly from start
    to end point, or uses explicit distances if provided.

    Args:
        states: List of states to arrange
        x1: X coordinate of line start point
        y1: Y coordinate of line start point
        x2: X coordinate of line end point
        y2: Y coordinate of line end point
        alignment: How to align each element relative to the line.
                  PRESERVE keeps original rotation, LAYOUT aligns parallel to line,
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        distances: Optional list of specific distances from center for each element.
                  If provided, overrides automatic distribution.
                  Positive values = forward along line, negative = backward along line.
        element_rotation_offset_fn: Optional function to calculate rotation offset dynamically.
                                    Not used currently, reserved for future compatibility.

    Returns:
        New list of states with line positions

    Raises:
        ValueError: If start and end points are identical (zero-length line)

    Examples:
        # Horizontal line from origin to (200, 0)
        >>> line_between_points(states, 0, 0, 200, 0)

        # Diagonal line
        >>> line_between_points(states, -100, -100, 100, 100)

        # Vertical line with elements aligned to line direction
        >>> line_between_points(states, 50, 0, 50, 200, alignment=ElementAlignment.LAYOUT)

        # Equivalent to line() with center and rotation:
        # line_between_points(states, 0, 0, 100, 100)
        # == line(states, cx=50, cy=50, rotation=45, spacing=~35.35)
    """
    if not states:
        return []

    # Calculate line vector
    dx = x2 - x1
    dy = y2 - y1

    # Check for zero-length line
    length = math.sqrt(dx * dx + dy * dy)
    if length < 1e-10:
        raise ValueError(
            f"Start point ({x1}, {y1}) and end point ({x2}, {y2}) are identical. "
            "Cannot create a line with zero length."
        )

    # Convert endpoints to center + rotation + spacing
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    rotation = math.degrees(math.atan2(dy, dx))
    spacing = length / (len(states) - 1) if len(states) > 1 else 0

    # Call canonical line function
    return line(
        states,
        spacing=spacing,
        rotation=rotation,
        cx=cx,
        cy=cy,
        distances=distances,
        alignment=alignment,
        element_rotation_offset=element_rotation_offset,
    )
