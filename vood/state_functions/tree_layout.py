"""Tree (hierarchy) layout state function"""

from typing import List, Optional, Callable
from dataclasses import replace
from vood.components import State
from .enums import ElementAlignment


def tree_layout(
    states: List[State],
    levels: Optional[List[int]] = None,
    children_per_node: int = 2,
    vertical_spacing: float = 100,
    horizontal_spacing: float = 100,
    center_x: float = 0,
    top_y: float = 0,
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation: float = 0,
    element_rotation_fn: Optional[Callable[[int, int], float]] = None,
) -> List[State]:
    """
    Arrange states in a tree (hierarchy) layout.

    Positions elements in levels, with each node having a fixed number of children.
    Preserves all other state properties (color, scale, opacity, etc.) while only
    modifying x and y positions.

    Args:
        states: List of states to arrange
        levels: Optional list specifying the level (depth) of each node. If not provided, nodes are assigned sequentially.
        children_per_node: Number of children per parent node
        vertical_spacing: Vertical distance between levels
        horizontal_spacing: Horizontal distance between sibling nodes
        center_x: X coordinate of tree center
        top_y: Y coordinate of top level
        alignment: How to align each element relative to the tree.
                  PRESERVE keeps original rotation, LAYOUT applies element_rotation,
                  UPRIGHT sets rotation to 0.
        element_rotation: Additional rotation in degrees added to the alignment base.
        element_rotation_fn: Function that takes (level, index) and returns rotation offset.
                           If provided, this overrides element_rotation parameter.

    Returns:
        New list of states with tree positions
    """
    if not states:
        return []

    num_elements = len(states)
    node_levels = levels if levels is not None else []
    if not node_levels:
        # Assign levels sequentially (simple binary tree)
        node_levels = []
        idx = 0
        level = 0
        count = 1
        while idx < num_elements:
            for _ in range(count):
                if idx < num_elements:
                    node_levels.append(level)
                    idx += 1
            level += 1
            count *= children_per_node

    # Count nodes per level
    from collections import Counter

    level_counts = Counter(node_levels)
    level_indices = {lvl: 0 for lvl in level_counts}

    result = []
    for i, state in enumerate(states):
        lvl = node_levels[i]
        count_in_level = level_counts[lvl]
        idx_in_level = level_indices[lvl]
        level_indices[lvl] += 1

        # Calculate horizontal position for node in its level
        total_width = (count_in_level - 1) * horizontal_spacing
        x = center_x + (idx_in_level * horizontal_spacing - total_width / 2)
        y = top_y + lvl * vertical_spacing

        if element_rotation_fn:
            additional_rotation = element_rotation_fn(lvl, idx_in_level)
        else:
            additional_rotation = element_rotation

        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            element_angle = additional_rotation
        elif alignment == ElementAlignment.UPRIGHT:
            element_angle = 0
        else:
            element_angle = state.rotation

        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result
