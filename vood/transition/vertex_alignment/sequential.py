"""Sequential alignment strategy for open shapes

This module provides an aligner for open ↔ open shape morphing with
reversal detection. Open shapes have natural sequential correspondence,
but may benefit from path reversal if oriented in opposite directions.
"""

from __future__ import annotations
from typing import List, Tuple
import math

from .base import VertexAligner, AlignmentContext
from vood.core.point2d import Point2D,Points2D

class SequentialAligner(VertexAligner):
    """Sequential alignment for open ↔ open shapes with reversal detection

    When both shapes are open, vertices have natural sequential correspondence
    (start to start, end to end). However, if the paths are oriented in opposite
    directions, reversing one path may produce a better morph.

    This aligner:
    1. Validates vertex counts match
    2. Compares total distance for normal vs reversed alignment
    3. Returns the orientation that minimizes total euclidean distance
    """

    @staticmethod
    def _calculate_total_distance(
        verts1: Points2D,
        verts2: Points2D
    ) -> float:
        """Calculate total euclidean distance between corresponding vertices

        Args:
            verts1: First vertex list
            verts2: Second vertex list (same length as verts1)

        Returns:
            Sum of euclidean distances between corresponding vertex pairs
        """
        total = 0.0
        for (x1, y1), (x2, y2) in zip(verts1, verts2):
            total += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return total

    def align(
        self,
        verts1: Points2D,
        verts2: Points2D,
        context: AlignmentContext,
        rotation_target: float | None = None,
    ) -> Tuple[Points2D, Points2D]:
        if len(verts1) != len(verts2):
            raise ValueError(
                f"Vertex lists must have same length: {len(verts1)} != {len(verts2)}"
            )

        # Calculate distance for normal orientation
        normal_distance = self._calculate_total_distance(verts1, verts2)

        # Calculate distance for reversed orientation
        verts2_reversed = list(reversed(verts2))
        reversed_distance = self._calculate_total_distance(verts1, verts2_reversed)

        # Return the orientation with smaller total distance
        if reversed_distance < normal_distance:
            return verts1, verts2_reversed
        else:
            return verts1, verts2

