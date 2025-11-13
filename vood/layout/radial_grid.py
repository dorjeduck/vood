"""Radial (polar) grid layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace
from vood.component import State
from .enums import ElementAlignment


def radial_grid(
    states: List[State],
    rings: int = 3,
    segments: int = 8,
    ring_spacing: float = 50,
    inner_radius: float = 50,
    center_x: float = 0,
    center_y: float = 0,
    rotation: float = 0,
    clockwise: bool = True,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[int, int, float], float]] = None,
    include_center: bool = False,
) -> List[State]:
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
        center_x: X coordinate of grid center
        center_y: Y coordinate of grid center
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
        
        new_state = replace(state, x=center_x, y=center_y, rotation=element_angle)
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
            x = center_x + radius * math.sin(angle_rad)
            y = center_y - radius * math.cos(angle_rad)
            
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