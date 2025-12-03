"""Utility functions for hole mapping

This module provides helper functions used by vertex_loop mapping strategies.
"""

from __future__ import annotations
from vood.component.vertex import VertexLoop


def create_zero_vertex_loop(reference_vertex_loop: VertexLoop) -> VertexLoop:
    """Create a zero-sized vertex_loop at the centroid of the reference vertex_loop

    All vertices are placed at the same point (the centroid), making a
    degenerate vertex_loop that can smoothly interpolate to/from the reference.

    This is used for vertex_loop creation/destruction scenarios:
    - N vertex loops → 0  vertex_loops : Each source vertex_loop shrinks to zero at its centroid
    - 0 vertex loops → M  vertex_loops : Each dest vertex_loop grows from zero at its centroid

    Args:
        reference_vertex_loop: vertex_loop to use as reference for position and vertex count

    Returns:
        Zero-sized VertexLoop with same vertex count as reference

    Example:
        >>> vertex_loop = VertexLoop([(0, 0), (10, 0), (10, 10), (0, 10)], closed=True)
        >>> zero = create_zero_vertex_loop(vertex_loop)
        >>> zero.vertices  # All at centroid (5, 5)
        [(5.0, 5.0), (5.0, 5.0), (5.0, 5.0), (5.0, 5.0)]
    """
    center = reference_vertex_loop.centroid()
    zero_vertices = [center] * len(reference_vertex_loop.vertices)
    return VertexLoop(zero_vertices, closed=True)
