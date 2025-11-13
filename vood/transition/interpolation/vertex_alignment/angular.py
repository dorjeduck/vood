"""Angular alignment strategy for closed shapes

This module provides angular-based alignment for closed ↔ closed shape morphing.
Uses centroid-based angular positions to find optimal vertex correspondence.
"""

from __future__ import annotations
from typing import List, Tuple

from vood.component.vertex import (
    centroid,
    angle_from_centroid,
    angle_distance,
    rotate_vertices,
)

from .base import VertexAligner, AlignmentContext


class AngularAligner(VertexAligner):
    """Angular alignment based on centroid positions

    Uses angular alignment based on vertex positions relative to centroids.
    Rotates the second vertex list to minimize total angular distance.
    Best for closed ↔ closed shape morphing.

    Algorithm:
    1. Apply shape rotations to both vertex lists
    2. Calculate centroids for each shape
    3. Compute angular positions of each vertex relative to its centroid
    4. Try all possible vertex offset rotations
    5. Select offset that minimizes total angular distance
    6. Return original vertices with selected offset applied to verts2

    Performance: O(n²) - tries n offsets, evaluates n vertices each
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

        if not verts1 or not verts2:
            return verts1, verts2

        # Apply shape rotations to vertices for alignment calculation
        verts1_rotated = rotate_vertices(verts1, context.rotation1)
        verts2_rotated = rotate_vertices(verts2, context.rotation2)

        # Calculate centroids
        c1 = centroid(verts1_rotated)
        c2 = centroid(verts2_rotated)

        # Get angular positions from centroids
        angles1 = [angle_from_centroid(v, c1) for v in verts1_rotated]
        angles2 = [angle_from_centroid(v, c2) for v in verts2_rotated]

        # Find rotation offset that minimizes total angular distance
        n = len(verts2)
        best_offset = 0
        min_distance = float("inf")

        for offset in range(n):
            total_dist = sum(
                angle_distance(angles1[i], angles2[(i + offset) % n]) for i in range(n)
            )

            if total_dist < min_distance:
                min_distance = total_dist
                best_offset = offset

        # Rotate verts2 (ORIGINAL, not rotated) by best_offset
        # We align the original vertices, not the rotated ones
        verts2_aligned = verts2[best_offset:] + verts2[:best_offset]

        return verts1, verts2_aligned
