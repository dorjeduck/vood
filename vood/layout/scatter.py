"""Random (scatter) layout state function"""

import random
from typing import List, Optional, Tuple
from dataclasses import replace
from vood.component import State
from .enums import ElementAlignment


def scatter(
    states: List[State],
    x_range: Tuple[float, float] = (-100, 100),
    y_range: Tuple[float, float] = (-100, 100),
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    seed: Optional[int] = None,
) -> List[State]:
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
