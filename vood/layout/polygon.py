"""Polygon layout state function"""

import math
from typing import List, Optional, Callable
from dataclasses import replace
from vood.component.state.base import States
from .enums import ElementAlignment


def polygon(
    states: States,
    sides: int = 5,
    radius: float = 100,
    rotation: float = 0,
    cx: float = 0,
    cy: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> States:
    """
    Arrange states evenly distributed around a regular polygon.
    Elements are placed at vertices and along edges based on distribution.

    Args:
        states: List of states to arrange
        sides: Number of sides (vertices) of the polygon
        radius: Distance from center to each vertex
        rotation: Rotation in degrees (0° = top)
        cx: X coordinate of polygon center
        cy: Y coordinate of polygon center
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
        x1 = cx + radius * math.sin(angle1_rad)
        y1 = cy - radius * math.cos(angle1_rad)
        x2 = cx + radius * math.sin(angle2_rad)
        y2 = cy - radius * math.cos(angle2_rad)

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


def polygon_in_bbox(
    states: States,
    x: float,
    y: float,
    width: float,
    height: float,
    sides: int = 6,
    rotation: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
) -> States:
    """
    Arrange states around a regular polygon inscribed in a bounding box.

    Alternative specification to polygon() for users who think in terms of bounding boxes.
    The polygon will be inscribed in the specified rectangle, with its size limited by
    the smaller dimension.

    Args:
        states: List of states to arrange
        x: X coordinate of bounding box top-left corner
        y: Y coordinate of bounding box top-left corner
        width: Width of bounding box
        height: Height of bounding box
        sides: Number of polygon sides
        rotation: Rotation offset in degrees
        alignment: How to align each element
        element_rotation_offset: Additional rotation offset
        element_rotation_offset_fn: Function(edge_angle) -> rotation offset

    Returns:
        New list of states with polygon positions

    Raises:
        ValueError: If sides < 3
        ValueError: If width or height is zero or negative

    Examples:
        # Hexagon in 400x400 box
        >>> polygon_in_bbox(states, 0, 0, 400, 400, sides=6)

        # Pentagon in rectangular box (limited by height)
        >>> polygon_in_bbox(states, -100, -150, 200, 300, sides=5)

        # Equivalent to polygon():
        # polygon_in_bbox(states, 0, 0, 400, 400, sides=6)
        # == polygon(states, cx=200, cy=200, radius=200, sides=6)
    """
    if not states:
        return []

    # Validate parameters
    if sides < 3:
        raise ValueError(f"Polygon must have at least 3 sides, got {sides}")
    if width <= 0:
        raise ValueError(f"Width must be positive, got {width}")
    if height <= 0:
        raise ValueError(f"Height must be positive, got {height}")

    # Convert bounding box to center + radius
    cx = x + width / 2
    cy = y + height / 2
    # Radius is limited by smaller dimension (inscribed polygon)
    radius = min(width, height) / 2

    # Call canonical polygon function
    return polygon(
        states,
        sides=sides,
        radius=radius,
        rotation=rotation,
        cx=cx,
        cy=cy,
        alignment=alignment,
        element_rotation_offset=element_rotation_offset,
        element_rotation_offset_fn=element_rotation_offset_fn,
    )
