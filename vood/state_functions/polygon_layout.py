"""Polygon layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace
from vood.components import State
from .enums import ElementAlignment


def polygon_layout(
    states: List[State],
    sides: int = 5,
    radius: float = 100,
    rotation: float = 0,
    center_x: float = 0,
    center_y: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation: float = 0,
    element_rotation_fn: Optional[Callable[[float], float]] = None,
    vertices_only: bool = True,
) -> List[State]:
    """
    Arrange states at the vertices or along the edges of a regular polygon.

    Args:
        states: List of states to arrange
        sides: Number of sides (vertices) of the polygon
        radius: Distance from center to each vertex
        rotation: Rotation in degrees (0° = top)
        center_x: X coordinate of polygon center
        center_y: Y coordinate of polygon center
        alignment: How to align each element relative to the polygon.
                  PRESERVE keeps original rotation, LAYOUT aligns tangent to edge,
                  UPRIGHT starts from vertical position.
        element_rotation: Additional rotation in degrees added to the alignment base.
        element_rotation_fn: Function that takes position angle (degrees) and returns rotation offset.
                           If provided, this overrides element_rotation parameter.
        vertices_only: If True, place elements only at vertices; if False, distribute along edges.

    Returns:
        New list of states with polygon positions
    """
    if not states or sides < 3:
        return []

    result = []
    num_elements = len(states)
    if vertices_only:
        # Place at vertices (repeat if more elements than vertices)
        for i, state in enumerate(states):
            vertex_idx = i % sides
            angle = rotation + 360 * vertex_idx / sides
            angle_rad = math.radians(angle)
            x = center_x + radius * math.sin(angle_rad)
            y = center_y - radius * math.cos(angle_rad)

            additional_rotation = (
                element_rotation_fn(angle) if element_rotation_fn else element_rotation
            )

            if alignment == ElementAlignment.PRESERVE:
                element_angle = state.rotation
            elif alignment == ElementAlignment.LAYOUT:
                # Tangent to edge (approximate by using angle + 90)
                element_angle = angle + 90 + additional_rotation
            elif alignment == ElementAlignment.UPRIGHT:
                element_angle = additional_rotation
            else:
                element_angle = state.rotation

            new_state = replace(state, x=x, y=y, rotation=element_angle)
            result.append(new_state)
    else:
        # Distribute along edges
        total_positions = num_elements
        for i, state in enumerate(states):
            # Find which edge and position along edge
            edge = (i * sides) // total_positions
            t = (i * sides) / total_positions - edge
            angle1 = rotation + 360 * edge / sides
            angle2 = rotation + 360 * ((edge + 1) % sides) / sides
            angle1_rad = math.radians(angle1)
            angle2_rad = math.radians(angle2)
            x1 = center_x + radius * math.sin(angle1_rad)
            y1 = center_y - radius * math.cos(angle1_rad)
            x2 = center_x + radius * math.sin(angle2_rad)
            y2 = center_y - radius * math.cos(angle2_rad)
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            angle = angle1 + t * (angle2 - angle1)
            additional_rotation = (
                element_rotation_fn(angle) if element_rotation_fn else element_rotation
            )

            if alignment == ElementAlignment.PRESERVE:
                element_angle = state.rotation
            elif alignment == ElementAlignment.LAYOUT:
                element_angle = angle + 90 + additional_rotation
            elif alignment == ElementAlignment.UPRIGHT:
                element_angle = additional_rotation
            else:
                element_angle = state.rotation

            new_state = replace(state, x=x, y=y, rotation=element_angle)
            result.append(new_state)

    return result
