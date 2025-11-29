"""Random (scatter) layout state function"""

import random
from typing import Optional, Tuple
from dataclasses import replace
from vood.component.state.base import States

from .enums import ElementAlignment


def scatter(
    states: States,
    x_range: Tuple[float, float] = (-100, 100),
    y_range: Tuple[float, float] = (-100, 100),
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    seed: Optional[int] = None,
) -> States:
    """
    Arrange states randomly (scatter) within a bounding box.

    Each element is placed at a random position within the specified x/y ranges.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        x_range: Tuple (min_x, max_x) for horizontal bounds
        y_range: Tuple (min_y, max_y) for vertical bounds
        alignment: How to align each element relative to the layout.
                  PRESERVE keeps original rotation, LAYOUT applies element_rotation_offset,
                  UPRIGHT sets rotation to 0.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        seed: Optional random seed for reproducibility

    Returns:
        New list of states with random positions
    """
    if not states:
        return []

    if seed is not None:
        random.seed(seed)

    result = []
    for state in states:
        x = random.uniform(*x_range)
        y = random.uniform(*y_range)

        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            element_angle = random.randint(0, 360) + element_rotation_offset
        elif alignment == ElementAlignment.UPRIGHT:
            element_angle = 0
        else:
            element_angle = state.rotation

        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result


def scatter_in_bbox(
    states: States,
    x: float,
    y: float,
    width: float,
    height: float,
    seed: Optional[int] = None,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
) -> States:
    """
    Arrange states randomly within a bounding box.

    Alternative specification to scatter() for users who think in terms of bounding boxes
    rather than min/max ranges. Elements will be randomly placed within the specified rectangle.

    Args:
        states: List of states to arrange
        x: X coordinate of bounding box top-left corner
        y: Y coordinate of bounding box top-left corner
        width: Width of bounding box
        height: Height of bounding box
        seed: Optional random seed for reproducibility
        alignment: How to align each element relative to the layout
        element_rotation_offset: Additional rotation in degrees added to the alignment base

    Returns:
        New list of states with random positions

    Raises:
        ValueError: If width or height is zero or negative

    Examples:
        # Random scatter in 400x300 box
        >>> scatter_in_bbox(states, 0, 0, 400, 300, seed=42)

        # Reproducible scatter in square area
        >>> scatter_in_bbox(states, -200, -200, 400, 400, seed=123)

        # Equivalent to scatter() with ranges:
        # scatter_in_bbox(states, 0, 0, 400, 300, seed=42)
        # == scatter(states, x_range=(0, 400), y_range=(0, 300), seed=42)
    """
    if not states:
        return []

    # Validate dimensions
    if width <= 0:
        raise ValueError(f"Width must be positive, got {width}")
    if height <= 0:
        raise ValueError(f"Height must be positive, got {height}")

    # Convert bounding box to ranges
    x_range = (x, x + width)
    y_range = (y, y + height)

    # Call canonical scatter function
    return scatter(
        states,
        x_range=x_range,
        y_range=y_range,
        alignment=alignment,
        element_rotation_offset=element_rotation_offset,
        seed=seed,
    )
