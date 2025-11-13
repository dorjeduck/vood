"""Euclidean distance alignment strategy for open/closed shape combinations

This module provides distance-based alignment for morphing between open and
closed shapes. Uses total Euclidean distance minimization rather than angular
alignment to preserve intuitive start-end correspondence.
"""

from __future__ import annotations
import math
from typing import List, Tuple

from .base import VertexAligner, AlignmentContext


class EuclideanAligner(VertexAligner):
    """Euclidean distance alignment for open ↔ closed shapes

    For open shapes (like lines), we minimize total Euclidean distance
    rather than angular distance. This preserves intuitive left-right
    or start-end correspondence.

    Algorithm:
    1. Identify which shape is open and which is closed
    2. Try all possible rotations of the closed shape
    3. For each rotation, calculate total Euclidean distance between all vertex pairs
    4. Select rotation that minimizes total distance
    5. Ensure last vertex equals first vertex for closed shape (closure)

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

        # Determine which is open and which is closed
        if not context.closed1 and context.closed2:
            # verts1 is open, verts2 is closed
            verts_open = verts1
            verts_closed = verts2
            swap = False
        elif context.closed1 and not context.closed2:
            # verts1 is closed, verts2 is open
            verts_open = verts2
            verts_closed = verts1
            swap = True
        else:
            # Both open or both closed - shouldn't use this aligner
            # Fall back to no alignment
            return verts1, verts2

        n = len(verts_closed)
        best_offset = 0
        min_distance = float("inf")

        # Try all rotations and find the one that minimizes total Euclidean distance
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

        # Rotate closed shape by best offset
        verts_closed_aligned = verts_closed[best_offset:] + verts_closed[:best_offset]

        # Make last vertex same as first for closed shape
        verts_closed_aligned[-1] = verts_closed_aligned[0]

        # Return in original order
        if swap:
            return verts_closed_aligned, verts_open
        else:
            return verts_open, verts_closed_aligned
