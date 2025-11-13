"""Pure functional wave layout for arranging elements along a sine wave"""

import math
from dataclasses import replace
from typing import List, Optional

from vood.component import State
from .enums import ElementAlignment


def wave(
    states: List[State],
    amplitude: float = 20,
    wavelength: float = 100,
    spacing: float = 50,
    phase: float = 0,
    middle_x: float = 0,
    middle_y: float = 0,
    rotation: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    distances: Optional[List[float]] = None,
) -> List[State]:
    """Arrange elements along a sine wave.

    Creates a new list of states with elements positioned along a sine wave,
    following the same base-line logic as line_layout but with wave displacement
    perpendicular to the line direction.

    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x, y positions and optionally rotation.

    Args:
        states: List of states to arrange
        amplitude: Height of the wave peaks
        wavelength: Distance between wave peaks
        spacing: Distance between adjacent elements along the base line
        phase: Phase shift of the wave in radians
        middle_x: X coordinate of the center point
        middle_y: Y coordinate of the center point
        rotation: Angle of the base line in degrees (0° = horizontal right)
        alignment: How to align each element relative to the wave base line.
                  PRESERVE keeps original rotation, LAYOUT aligns parallel to base line,
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        distances: Optional list of specific distances from center for each element.
                  If provided, overrides automatic spacing calculation.
                  List length should match states length.

    Returns:
        New list of states with wave positions

    Examples:
        # Basic horizontal wave
        >>> states = [CircleState(), CircleState(), CircleState()]
        >>> wave_layout(states, amplitude=30, wavelength=200)

        # Diagonal wave with custom spacing
        >>> wave_layout(states, rotation=45, spacing=40, amplitude=20)

        # Wave with custom distances
        >>> wave_layout(states, distances=[-100, -50, 0, 50, 100])
    """
    if not states:
        return []

    result = []
    num_elements = len(states)

    # Use custom distances if provided, otherwise calculate even distribution
    if distances is not None:
        if len(distances) < len(states):
            raise ValueError(
                f"Length of distances ({len(distances)}) must be equal or bigger than length of states ({len(states)})"
            )
        line_positions = distances
    else:
        # Calculate positions along the base line

        if num_elements % 2 == 1:
            # Odd number of elements - one at center
            center_index = num_elements // 2
            line_positions = [(i - center_index) * spacing for i in range(num_elements)]
        else:
            # Even number of elements - symmetric around center
            line_positions = [
                (i - (num_elements - 1) / 2) * spacing for i in range(num_elements)
            ]

    # Convert rotation to radians and precompute trigonometric values
    angle_rad = math.radians(rotation)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)

    # Position each element along the wave
    for i, state in enumerate(states):
        line_pos = line_positions[i]

        # Calculate base position along the line
        base_x = middle_x + line_pos * cos_angle
        base_y = middle_y + line_pos * sin_angle

        # Calculate wave offset perpendicular to the line
        wave_offset = amplitude * math.sin(
            (2 * math.pi / wavelength) * line_pos + phase
        )

        # Apply wave offset in perpendicular direction
        # Perpendicular direction components (rotated 90° from line direction)
        perp_x = -sin_angle
        perp_y = cos_angle

        x = base_x + wave_offset * perp_x
        y = base_y + wave_offset * perp_y

        # Calculate element rotation based on alignment mode
        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            # Align with base line direction + additional rotation
            element_angle = rotation + element_rotation_offset
        elif alignment == ElementAlignment.UPRIGHT:
            # Start from upright position + additional rotation
            element_angle = element_rotation_offset
        else:
            element_angle = state.rotation

        # Create new state with wave position and rotation, preserving all other properties
        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result
