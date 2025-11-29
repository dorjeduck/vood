"""Radial (polar) grid layout state function"""

import math
from typing import Optional, Callable
from dataclasses import replace
from vood.component.state.base import States

from .enums import ElementAlignment


def radial_grid(
    states: States,
    rings: int = 3,
    segments: int = 8,
    ring_spacing: float = 50,
    inner_radius: float = 50,
    cx: float = 0,
    cy: float = 0,
    rotation: float = 0,
    clockwise: bool = True,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[int, int, float], float]] = None,
    include_center: bool = False,
) -> States:
    """
    Arrange states in a radial (polar coordinate) grid with rings and segments.

    Creates a circular grid with concentric rings divided into equal angular segments.
    Elements are placed at the intersection of each ring and segment.

    Args:
        states: List of states to arrange
        rings: Number of concentric rings
        segments: Number of angular segments (divisions around the circle)
        ring_spacing: Distance between consecutive rings
        inner_radius: Radius of the innermost ring (set to 0 to start from center)
        cx: X coordinate of grid center
        cy: Y coordinate of grid center
        rotation: Rotation offset in degrees (0° = top)
        clockwise: If True, segments arranged clockwise; if False, counterclockwise
        alignment: How to align each element relative to the grid.
                  PRESERVE keeps original rotation, LAYOUT aligns radially outward,
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        element_rotation_offset_fn: Function that takes (ring_index, segment_index, angle)
                           and returns rotation offset. If provided, overrides element_rotation_offset.
        include_center: If True, place first element at center point (0,0)

    Returns:
        New list of states with radial grid positions

    Examples:
        # Simple radial grid
        >>> radial_grid(states, rings=3, segments=8)

        # Radial grid with center element
        >>> radial_grid(states, rings=3, segments=6, include_center=True)

        # Elements pointing outward from center
        >>> radial_grid(states, rings=4, segments=12, alignment=ElementAlignment.LAYOUT)
    """
    if not states:
        return []

    result = []
    state_idx = 0

    # Place center element if requested
    if include_center and state_idx < len(states):
        state = states[state_idx]

        additional_rotation = (
            element_rotation_offset_fn(0, 0, 0)
            if element_rotation_offset_fn
            else element_rotation_offset
        )

        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            element_angle = additional_rotation
        elif alignment == ElementAlignment.UPRIGHT:
            element_angle = additional_rotation
        else:
            element_angle = state.rotation

        new_state = replace(state, x=cx, y=cy, rotation=element_angle)
        result.append(new_state)
        state_idx += 1

    # Place elements in rings
    for ring in range(rings):
        if state_idx >= len(states):
            break

        radius = inner_radius + ring * ring_spacing
        angle_step = 360 / segments

        for seg in range(segments):
            if state_idx >= len(states):
                break

            state = states[state_idx]

            # Calculate angle for this segment
            angle = rotation + (seg * angle_step if clockwise else -seg * angle_step)
            angle_rad = math.radians(angle)

            # Calculate position
            x = cx + radius * math.sin(angle_rad)
            y = cy - radius * math.cos(angle_rad)

            # Calculate rotation
            additional_rotation = (
                element_rotation_offset_fn(ring, seg, angle)
                if element_rotation_offset_fn
                else element_rotation_offset
            )

            if alignment == ElementAlignment.PRESERVE:
                element_angle = state.rotation
            elif alignment == ElementAlignment.LAYOUT:
                # Point radially outward from center
                element_angle = angle + additional_rotation
            elif alignment == ElementAlignment.UPRIGHT:
                element_angle = additional_rotation
            else:
                element_angle = state.rotation

            new_state = replace(state, x=x, y=y, rotation=element_angle)
            result.append(new_state)
            state_idx += 1

    return result


def radial_grid_between_radii(
    states: States,
    cx: float = 0,
    cy: float = 0,
    inner_radius: float = 50,
    outer_radius: float = 200,
    rings: int = 3,
    segments: int = 8,
    rotation: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[int, int, float], float]] = None,
) -> States:
    """
    Arrange states in a radial grid with specified inner and outer radii.

    Alternative specification to radial_grid() for users who think in terms of
    target outer radius rather than ring spacing. The rings will be evenly
    distributed between the inner and outer radii.

    Args:
        states: List of states to arrange
        cx: X coordinate of grid center
        cy: Y coordinate of grid center
        inner_radius: Radius of innermost ring
        outer_radius: Radius of outermost ring
        rings: Number of concentric rings
        segments: Number of angular segments per ring
        rotation: Base rotation in degrees
        alignment: How to align each element
        element_rotation_offset: Additional rotation offset
        element_rotation_offset_fn: Function(ring, seg, angle) -> rotation offset

    Returns:
        New list of states with radial grid positions

    Raises:
        ValueError: If outer_radius <= inner_radius
        ValueError: If rings < 1

    Examples:
        # Grid from radius 50 to 200 with 4 rings
        >>> radial_grid_between_radii(states, inner_radius=50, outer_radius=200, rings=4, segments=8)

        # Equivalent to radial_grid():
        # radial_grid_between_radii(states, inner_radius=50, outer_radius=200, rings=3)
        # == radial_grid(states, inner_radius=50, ring_spacing=75, rings=3)
    """
    if not states:
        return []

    if outer_radius <= inner_radius:
        raise ValueError(
            f"outer_radius ({outer_radius}) must be greater than inner_radius ({inner_radius})"
        )
    if rings < 1:
        raise ValueError(f"rings must be at least 1, got {rings}")

    # Calculate ring spacing to fit between inner and outer radii
    ring_spacing = (outer_radius - inner_radius) / rings if rings > 0 else 0

    # Call canonical radial_grid function
    return radial_grid(
        states,
        rings=rings,
        segments=segments,
        ring_spacing=ring_spacing,
        inner_radius=inner_radius,
        cx=cx,
        cy=cy,
        rotation=rotation,
        alignment=alignment,
        element_rotation_offset=element_rotation_offset,
        element_rotation_offset_fn=element_rotation_offset_fn,
    )
