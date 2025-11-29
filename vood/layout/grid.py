"""Grid layout state function"""

from typing import Optional
from dataclasses import replace
from vood.component.state.base import States

from .enums import ElementAlignment


def grid(
    states: States,
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    spacing_h: float = 100,
    spacing_v: float = 100,
    cx: float = 0,
    cy: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
) -> States:
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
        cx: X coordinate of grid center
        cy: Y coordinate of grid center
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
        x = cx + (col * spacing_h - grid_width / 2)
        y = cy + (row * spacing_v - grid_height / 2)

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


def grid_in_bbox(
    states: States,
    x: float,
    y: float,
    width: float,
    height: float,
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
) -> States:
    """
    Arrange states in a rectangular grid that fits within a bounding box.

    Alternative specification to grid() for users who think in terms of available space
    rather than spacing between elements. The grid will be sized to fill the specified
    bounding box with elements evenly distributed.

    Args:
        states: List of states to arrange
        x: X coordinate of bounding box top-left corner
        y: Y coordinate of bounding box top-left corner
        width: Width of bounding box
        height: Height of bounding box
        rows: Number of rows in the grid (optional, auto-calculated if not provided)
        cols: Number of columns in the grid (optional, auto-calculated if not provided)
        alignment: How to align each element relative to the grid
        element_rotation_offset: Additional rotation in degrees added to the alignment base

    Returns:
        New list of states with grid positions

    Raises:
        ValueError: If width or height is zero or negative

    Examples:
        # 3x3 grid in 600x600 box
        >>> grid_in_bbox(states, 0, 0, 600, 600, rows=3, cols=3)

        # Auto-sized grid filling rectangular area
        >>> grid_in_bbox(states, -200, -150, 400, 300)

        # Equivalent to grid() with spacing:
        # grid_in_bbox(states, 0, 0, 400, 200, rows=3, cols=4)
        # == grid(states, rows=3, cols=4, cx=200, cy=100, spacing_h=~133, spacing_v=100)
    """
    if not states:
        return []

    # Validate dimensions
    if width <= 0:
        raise ValueError(f"Width must be positive, got {width}")
    if height <= 0:
        raise ValueError(f"Height must be positive, got {height}")

    num_elements = len(states)

    # Determine grid size (same logic as grid())
    if rows is None and cols is None:
        cols = int(num_elements**0.5)
        rows = (num_elements + cols - 1) // cols
    elif rows is None:
        rows = (num_elements + cols - 1) // cols
    elif cols is None:
        cols = (num_elements + rows - 1) // rows

    # Calculate spacing to fit in bbox
    spacing_h = width / (cols - 1) if cols > 1 else 0
    spacing_v = height / (rows - 1) if rows > 1 else 0

    # Center is at bbox center
    cx = x + width / 2
    cy = y + height / 2

    # Call canonical grid function
    return grid(
        states,
        rows=rows,
        cols=cols,
        spacing_h=spacing_h,
        spacing_v=spacing_v,
        cx=cx,
        cy=cy,
        alignment=alignment,
        element_rotation_offset=element_rotation_offset,
    )
