"""Line layout state function"""

import math
from typing import List, Optional
from dataclasses import replace

from vood.component import State
from .enums import ElementAlignment


def line(
    states: List[State],
    spacing: float = 100,
    rotation: float = 0,
    center_x: float = 0,
    center_y: float = 0,
    distances: Optional[List[float]] = None,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
) -> List[State]:
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
        center_x: X coordinate of line center
        center_y: Y coordinate of line center
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
        x = center_x + line_pos * cos_rotation
        y = center_y + line_pos * sin_rotation

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
