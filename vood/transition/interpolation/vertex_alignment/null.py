"""Null alignment strategy for open shapes

This module provides a pass-through aligner for open ↔ open shape morphing.
No alignment is needed since open shapes have natural correspondence.
"""

from __future__ import annotations
from typing import List, Tuple

from .base import VertexAligner, AlignmentContext


class NullAligner(VertexAligner):
    """No alignment for open ↔ open shapes

    When both shapes are open, vertices already have natural correspondence
    (start to start, end to end), so no alignment is needed.

    This is essentially a pass-through that validates vertex counts match
    and returns the vertices unchanged.
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
        return verts1, verts2
