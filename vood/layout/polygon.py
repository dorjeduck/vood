"""Polygon layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace
from vood.component import State
from .enums import ElementAlignment


def polygon(
    states: List[State],
    sides: int = 5,
    radius: float = 100,
    rotation: float = 0,
    center_x: float = 0,
    center_y: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> List[State]:
    """
    Arrange states evenly distributed around a regular polygon.
    Elements are placed at vertices and along edges based on distribution.

    Args:
        states: List of states to arrange
        sides: Number of sides (vertices) of the polygon
        radius: Distance from center to each vertex
        rotation: Rotation in degrees (0° = top)
        center_x: X coordinate of polygon center
        center_y: Y coordinate of polygon center
        alignment: How to align each element relative to the polygon.
                  PRESERVE keeps original rotation,
                  LAYOUT aligns to edge angle (or perpendicular at vertices),
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        element_rotation_offset_fn: Function that takes position angle (degrees) and returns rotation offset.
                           If provided, this overrides element_rotation_offset parameter.

    Returns:
        New list of states with polygon positions
    """
    if not states or sides < 3:
        return []

    result = []
    num_elements = len(states)

    # Distribute elements evenly around the polygon perimeter
    for i, state in enumerate(states):
        # Calculate position as a fraction around the polygon (0 to sides)
        position = (i * sides) / num_elements

        # Determine which edge and position along that edge
        edge = int(position) % sides
        t = position - int(
            position
        )  # Position along edge (0 = at first vertex, 1 = at second vertex)

        # Get the two vertices of this edge
        angle1 = rotation + 360 * edge / sides
        angle2 = rotation + 360 * ((edge + 1) % sides) / sides
        angle1_rad = math.radians(angle1)
        angle2_rad = math.radians(angle2)

        # Calculate vertex positions
        x1 = center_x + radius * math.sin(angle1_rad)
        y1 = center_y - radius * math.cos(angle1_rad)
        x2 = center_x + radius * math.sin(angle2_rad)
        y2 = center_y - radius * math.cos(angle2_rad)

        # Interpolate position along edge
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)

        # Calculate edge angle (direction from vertex1 to vertex2)
        edge_angle = math.degrees(math.atan2(x2 - x1, -(y2 - y1)))

        # Determine if we're at a vertex (t is very close to 0)
        at_vertex = t < 0.01

        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
            additional_rotation = (
                element_rotation_offset_fn(edge_angle)
                if element_rotation_offset_fn
                else element_rotation_offset
            )
            element_angle += additional_rotation
        elif alignment == ElementAlignment.LAYOUT:
            if at_vertex:
                # At vertex: rotate perpendicular to edge (90° from edge angle)
                element_angle = edge_angle - 90 - 180 / sides
            else:
                # On edge: align parallel to edge
                element_angle = edge_angle - 90

            additional_rotation = (
                element_rotation_offset_fn(edge_angle)
                if element_rotation_offset_fn
                else element_rotation_offset
            )
            element_angle += additional_rotation
        elif alignment == ElementAlignment.UPRIGHT:
            additional_rotation = (
                element_rotation_offset_fn(edge_angle)
                if element_rotation_offset_fn
                else element_rotation_offset
            )
            element_angle = additional_rotation
        else:
            element_angle = state.rotation

        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result
