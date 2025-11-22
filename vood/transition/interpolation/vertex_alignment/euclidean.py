"""Euclidean distance alignment strategy for open/closed shape combinations

This module provides distance-based alignment for morphing between open and
closed shapes. Uses total Euclidean distance minimization rather than angular
alignment to preserve intuitive start-end correspondence.
"""

from __future__ import annotations
import math
from typing import List, Tuple

from vood.component.vertex import rotate_vertices
from .base import VertexAligner, AlignmentContext


class EuclideanAligner(VertexAligner):
    """Euclidean distance alignment for open ↔ closed shapes

    For open shapes (like lines), we minimize total Euclidean distance
    rather than angular distance. This preserves intuitive left-right
    or start-end correspondence.

    Algorithm:
    1. Apply shape rotations to both vertex lists
    2. Identify which shape is open and which is closed
    3. Try all possible rotations of the closed shape
    4. For each rotation, calculate total Euclidean distance between all vertex pairs
    5. Select rotation that minimizes total distance
    6. Return original vertices with selected offset applied
    7. Ensure last vertex equals first vertex for closed shape (closure)

    Performance: O(n²) - tries n offsets, evaluates n vertex pairs each
    """

    def align(
        self,
        verts1: List[Tuple[float, float]],
        verts2: List[Tuple[float, float]],
        context: AlignmentContext
    ) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        if len(verts1) != len(verts2):
            raise ValueError(
                f"Vertex lists must have same length: {len(verts1)} != {len(verts2)}"
            )

        # Apply shape rotations to vertices for alignment calculation
        # (consistent with AngularAligner)
        verts1_rotated = rotate_vertices(verts1, context.rotation1)
        verts2_rotated = rotate_vertices(verts2, context.rotation2)

        # Determine which is open and which is closed
        if not context.closed1 and context.closed2:
            # verts1 is open, verts2 is closed
            verts_open = verts1_rotated
            verts_closed = verts2_rotated
            verts_open_original = verts1
            verts_closed_original = verts2
            swap = False
        elif context.closed1 and not context.closed2:
            # verts1 is closed, verts2 is open
            verts_open = verts2_rotated
            verts_closed = verts1_rotated
            verts_open_original = verts2
            verts_closed_original = verts1
            swap = True
        else:
            # Both open or both closed - shouldn't use this aligner
            # Fall back to no alignment
            return verts1, verts2

        n = len(verts_closed)
        best_offset = 0
        min_distance = float("inf")

        # Try all rotations and find the one that minimizes total Euclidean distance
        # Use rotated vertices for distance calculation
        for offset in range(n):
            total_dist = sum(
                math.sqrt(
                    (verts_open[i][0] - verts_closed[(i + offset) % n][0]) ** 2
                    + (verts_open[i][1] - verts_closed[(i + offset) % n][1]) ** 2
                )
                for i in range(n)
            )

            if total_dist < min_distance:
                min_distance = total_dist
                best_offset = offset

        # Apply best offset to ORIGINAL vertices (not rotated)
        # This is consistent with AngularAligner behavior
        verts_closed_aligned = (
            verts_closed_original[best_offset:] + verts_closed_original[:best_offset]
        )

        # Make last vertex same as first for closed shape
        verts_closed_aligned[-1] = verts_closed_aligned[0]

        # Return original vertices in original order
        if swap:
            return verts_closed_aligned, verts_open_original
        else:
            return verts_open_original, verts_closed_aligned
