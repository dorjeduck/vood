"""Pure functional wave layout for arranging elements along a sine wave"""

import math
from dataclasses import replace
from typing import List, Optional, Callable

from vood.component.state.base import States
from .enums import ElementAlignment


def wave(
    states: States,
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
) -> States:
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


def wave_between_points(
    states: States,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    amplitude: float = 50,
    wavelength: float = 200,
    phase: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    distances: Optional[List[float]] = None,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> States:
    """
    Arrange states along a sine wave from point A to point B.

    Alternative specification to wave() for users who think in terms of endpoints.
    Distributes states evenly from start to end point along a wave pattern, with
    the wave oscillating perpendicular to the line between the points.

    Args:
        states: List of states to arrange
        x1: X coordinate of wave base line start point
        y1: Y coordinate of wave base line start point
        x2: X coordinate of wave base line end point
        y2: Y coordinate of wave base line end point
        amplitude: Height of the wave peaks
        wavelength: Distance between wave peaks
        phase: Phase shift of the wave in radians
        alignment: How to align each element relative to the wave base line.
                  PRESERVE keeps original rotation, LAYOUT aligns parallel to base line,
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        distances: Optional list of specific distances from center for each element.
                  If provided, overrides automatic distribution.
        element_rotation_offset_fn: Optional function to calculate rotation offset dynamically.
                                    Not used currently, reserved for future compatibility.

    Returns:
        New list of states with wave positions

    Raises:
        ValueError: If start and end points are identical (zero-length base line)

    Examples:
        # Horizontal wave from origin to (200, 0)
        >>> wave_between_points(states, 0, 0, 200, 0, amplitude=30, wavelength=100)

        # Diagonal wave
        >>> wave_between_points(states, -100, -100, 100, 100, amplitude=20)

        # Vertical wave with custom wavelength
        >>> wave_between_points(states, 50, 0, 50, 200, amplitude=40, wavelength=150)

        # Equivalent to wave() with center and rotation:
        # wave_between_points(states, 0, 0, 200, 0, amplitude=30)
        # == wave(states, middle_x=100, middle_y=0, rotation=0, amplitude=30, spacing=~50)
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
            "Cannot create a wave with zero-length base line."
        )

    # Convert endpoints to middle + rotation + spacing
    middle_x = (x1 + x2) / 2
    middle_y = (y1 + y2) / 2
    rotation = math.degrees(math.atan2(dy, dx))
    spacing = length / (len(states) - 1) if len(states) > 1 else 0

    # Call canonical wave function
    return wave(
        states,
        amplitude=amplitude,
        wavelength=wavelength,
        spacing=spacing,
        phase=phase,
        middle_x=middle_x,
        middle_y=middle_y,
        rotation=rotation,
        alignment=alignment,
        element_rotation_offset=element_rotation_offset,
        distances=distances,
    )
