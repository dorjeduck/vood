"""Euclidean distance alignment strategy for open/closed shape combinations

This module provides distance-based alignment for morphing between open and
closed shapes. Uses total Euclidean distance minimization rather than angular
alignment to preserve intuitive start-end correspondence.
"""

from __future__ import annotations
import math
import logging
from typing import List, Tuple, Optional, Union, Callable
import inspect

from vood.component.vertex import rotate_vertices_inplace, rotate_list_inplace
from .base import VertexAligner, AlignmentContext
from .norm import AlignmentNorm, EuclideanDistanceFn, NormSpec
from vood.core.point2d import Points2D, Point2D

logger = logging.getLogger(__name__)

class EuclideanAligner(VertexAligner):
    """Euclidean distance alignment for open ↔ closed shapes

    For open shapes (like lines), we minimize total Euclidean distance
    rather than angular distance. This preserves intuitive left-right
    or start-end correspondence.

    Algorithm:
    1. Apply shape rotations to both vertex lists
    2. Identify which shape is open and which is closed
    3. Try all possible rotations of the closed shape
    4. For each rotation, calculate total Euclidean distance between all vertex pairs (using specified norm)
    5. Select rotation that minimizes total distance
    6. Return original vertices with selected offset applied
    7. Ensure last vertex equals first vertex for closed shape (closure)

    Performance: O(n²) - tries n offsets, evaluates n vertex pairs each
    """

    def __init__(self, norm: Union[str, AlignmentNorm, EuclideanDistanceFn] = "l1"):
        """
        Initialize Euclidean aligner with distance norm.

        Args:
            norm: Distance metric for alignment
                - "l1" or AlignmentNorm.L1: Sum of Euclidean distances (default)
                - "l2" or AlignmentNorm.L2: Root mean square Euclidean distance
                - "linf" or AlignmentNorm.LINF: Maximum Euclidean distance
                - Callable: Custom distance function(verts1, verts2, offset) -> float
        """
        if callable(norm):
            # Validate callable signature
            sig = inspect.signature(norm)
            if len(sig.parameters) != 3:
                raise TypeError(
                    f"Custom distance function must accept 3 parameters: "
                    f"(verts1, verts2, offset), got {len(sig.parameters)}"
                )
            self.norm = "custom"
            self._distance_fn = norm
        elif isinstance(norm, (str, AlignmentNorm)):
            self.norm = norm
            self._distance_fn = self._resolve_distance_function(norm)
        else:
            raise TypeError(
                f"norm must be str, AlignmentNorm, or callable, "
                f"got {type(norm).__name__}"
            )

    def _resolve_distance_function(self, norm: Union[str, AlignmentNorm]) -> EuclideanDistanceFn:
        """Convert norm spec to actual distance function"""
        # Normalize string to enum
        if isinstance(norm, str):
            try:
                norm = AlignmentNorm(norm.lower())
            except ValueError:
                raise ValueError(
                    f"Invalid norm '{norm}'. Valid options: 'l1', 'l2', 'linf'"
                )

        # Return built-in function
        if norm == AlignmentNorm.L1:
            return self._l1_distance
        elif norm == AlignmentNorm.L2:
            return self._l2_distance
        elif norm == AlignmentNorm.LINF:
            return self._linf_distance
        else:
            raise ValueError(f"Unknown norm: {norm}")

    def _l1_distance(self, verts1: Points2D, verts2: Points2D, offset: int) -> float:
        """Sum of Euclidean distances (L1 norm of L2 distances)"""
        n = len(verts1)
        return sum(
            math.sqrt(
                (verts1[i].x - verts2[(i + offset) % n].x) ** 2
                + (verts1[i].y - verts2[(i + offset) % n].y) ** 2
            )
            for i in range(n)
        )

    def _l2_distance(self, verts1: Points2D, verts2: Points2D, offset: int) -> float:
        """Root mean square Euclidean distance (L2 norm of L2 distances)"""
        n = len(verts1)
        return math.sqrt(sum(
            (verts1[i].x - verts2[(i + offset) % n].x) ** 2
            + (verts1[i].y - verts2[(i + offset) % n].y) ** 2
            for i in range(n)
        ))

    def _linf_distance(self, verts1: Points2D, verts2: Points2D, offset: int) -> float:
        """Maximum Euclidean distance (L∞ norm of L2 distances, minimax)"""
        n = len(verts1)
        return max(
            math.sqrt(
                (verts1[i].x - verts2[(i + offset) % n].x) ** 2
                + (verts1[i].y - verts2[(i + offset) % n].y) ** 2
            )
            for i in range(n)
        )

    def align(
        self,
        verts1: Points2D,
        verts2: Points2D,
        context: AlignmentContext,
        rotation_target: Optional[float] = None,
    ) -> Tuple[Points2D, Points2D]:
        if len(verts1) != len(verts2):
            raise ValueError(
                f"Vertex lists must have same length: {len(verts1)} != {len(verts2)}"
            )

        # Use rotation_target if provided, otherwise use context rotations
        rot1 = context.rotation1
        rot2 = rotation_target if rotation_target is not None else context.rotation2

        # Create working copies for rotation (only if needed)
        if rot1 != 0 or rot2 != 0:
            verts1_work = [Point2D(v.x, v.y) for v in verts1]
            verts2_work = [Point2D(v.x, v.y) for v in verts2]

            if rot1 != 0:
                rotate_vertices_inplace(verts1_work, rot1)
            if rot2 != 0:
                rotate_vertices_inplace(verts2_work, rot2)
        else:
            verts1_work = verts1
            verts2_work = verts2

        # Determine which is open and which is closed
        if not context.closed1 and context.closed2:
            # verts1 is open, verts2 is closed
            verts_open_work = verts1_work
            verts_closed_work = verts2_work
            verts_open_original = verts1
            verts_closed_original = verts2
            swap = False
        elif context.closed1 and not context.closed2:
            # verts1 is closed, verts2 is open
            verts_open_work = verts2_work
            verts_closed_work = verts1_work
            verts_open_original = verts2
            verts_closed_original = verts1
            swap = True
        else:
            # Both open or both closed - shouldn't use this aligner
            closure_state = "both closed" if context.closed1 else "both open"
            logger.error(
                f"EuclideanAligner called with {closure_state} shapes. "
                f"This aligner is only for open ↔ closed combinations. "
                f"Use AngularAligner for closed ↔ closed or SequentialAligner for open ↔ open. "
                f"Returning unaligned vertices."
            )
            return verts1, verts2

        n = len(verts_closed_work)
        best_offset = 0
        min_distance = float("inf")

        # Try all rotations and find the one that minimizes total Euclidean distance (using specified norm)
        for offset in range(n):
            # Use configured distance function (L1, L2, L∞, or custom)
            total_dist = self._distance_fn(verts_open_work, verts_closed_work, offset)

            if total_dist < min_distance:
                min_distance = total_dist
                best_offset = offset

        # Apply best offset to original vertices using in-place rotation
        if best_offset == 0:
            verts_closed_aligned = list(verts_closed_original)  # Make a copy
        else:
            verts_closed_aligned = list(verts_closed_original)
            rotate_list_inplace(verts_closed_aligned, best_offset)

        # Make last vertex same as first for closed shape
        verts_closed_aligned[-1] = verts_closed_aligned[0]

        # Return vertices in original order
        if swap:
            return verts_closed_aligned, verts_open_original
        else:
            return verts_open_original, verts_closed_aligned
