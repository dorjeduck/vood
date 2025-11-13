"""Grid layout state function"""

from typing import List, Optional
from dataclasses import replace
from vood.component import State
from .enums import ElementAlignment


def grid(
    states: List[State],
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    spacing_h: float = 100,
    spacing_v: float = 100,
    center_x: float = 0,
    center_y: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
) -> List[State]:
    """
    Arrange states in a rectangular grid formation.

    Positions elements in a grid with configurable spacing, center, and alignment.
    If rows or cols are not provided, the function will attempt to create a nearly square grid.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        rows: Number of rows in the grid (optional)
        cols: Number of columns in the grid (optional)
        spacing_h: Horizontal spacing between elements
        spacing_v: Vertical spacing between elements
        center_x: X coordinate of grid center
        center_y: Y coordinate of grid center
        alignment: How to align each element relative to the grid.
                  PRESERVE keeps original rotation, LAYOUT aligns with grid axes,
                  UPRIGHT starts from vertical position.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.

    Returns:
        New list of states with grid positions
    """
    if not states:
        return []

    num_elements = len(states)

    # Determine grid size
    if rows is None and cols is None:
        cols = int(num_elements**0.5)
        rows = (num_elements + cols - 1) // cols
    elif rows is None:
        rows = (num_elements + cols - 1) // cols
    elif cols is None:
        cols = (num_elements + rows - 1) // rows

    result = []
    for idx, state in enumerate(states):
        row = idx // cols
        col = idx % cols

        # Calculate position relative to grid center
        grid_width = (cols - 1) * spacing_h
        grid_height = (rows - 1) * spacing_v
        x = center_x + (col * spacing_h - grid_width / 2)
        y = center_y + (row * spacing_v - grid_height / 2)

        # Calculate element rotation based on alignment mode
        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            element_angle = element_rotation_offset
        elif alignment == ElementAlignment.UPRIGHT:
            element_angle = 0
        else:
            element_angle = state.rotation

        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result
