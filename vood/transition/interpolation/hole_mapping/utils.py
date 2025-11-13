"""Utility functions for hole mapping

This module provides helper functions used by hole mapping strategies.
"""

from __future__ import annotations
from vood.component.vertex import VertexLoop


def create_zero_hole(reference_hole: VertexLoop) -> VertexLoop:
    """Create a zero-sized hole at the centroid of the reference hole

    All vertices are placed at the same point (the centroid), making a
    degenerate hole that can smoothly interpolate to/from the reference.

    This is used for hole creation/destruction scenarios:
    - N holes → 0 holes: Each source hole shrinks to zero at its centroid
    - 0 holes → M holes: Each dest hole grows from zero at its centroid

    Args:
        reference_hole: Hole to use as reference for position and vertex count

    Returns:
        Zero-sized VertexLoop with same vertex count as reference

    Example:
        >>> hole = VertexLoop([(0, 0), (10, 0), (10, 10), (0, 10)], closed=True)
        >>> zero = create_zero_hole(hole)
        >>> zero.vertices  # All at centroid (5, 5)
        [(5.0, 5.0), (5.0, 5.0), (5.0, 5.0), (5.0, 5.0)]
    """
    center = reference_hole.centroid()
    zero_vertices = [center] * len(reference_hole.vertices)
    return VertexLoop(zero_vertices, closed=True)
