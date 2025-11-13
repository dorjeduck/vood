"""Greedy nearest-centroid hole mapping strategy

This module provides the default hole mapping implementation using a simple
greedy nearest-neighbor approach based on centroid distances.
"""

from __future__ import annotations
import math
from typing import List, Tuple

from vood.component.vertex import VertexLoop
from .base import HoleMapper
from .utils import create_zero_hole


class GreedyNearestMapper(HoleMapper):
    """Match holes using greedy nearest-centroid strategy

    Uses a simple greedy approach to match holes based on centroid distances.
    This is fast (O(n²)) and works well for most cases.

    Handles different hole counts:
    - N = M: Greedy 1:1 pairing by nearest centroids
    - N > M: Multiple sources merge to single dest (each source finds nearest dest)
    - N < M: Single source splits to multiple dests (each dest finds nearest source)
    - N = 0 or M = 0: Holes shrink/grow at their centroids

    Algorithm:
    - For equal counts: Greedy matching without replacement (each hole used once)
    - For unequal counts: Greedy matching with replacement (holes can be reused)

    Note: This may not give globally optimal results. For better matching,
    consider HungarianMapper (when implemented).
    """

    def map(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        n1 = len(holes1)
        n2 = len(holes2)

        # Case 1: No holes on either side
        if n1 == 0 and n2 == 0:
            return [], []

        # Case 2: Source has holes, dest has none (holes disappear)
        if n1 > 0 and n2 == 0:
            # Each source hole shrinks to zero at its own position
            matched_holes1 = holes1.copy()
            matched_holes2 = [create_zero_hole(hole) for hole in holes1]
            return matched_holes1, matched_holes2

        # Case 3: Source has no holes, dest has holes (holes appear)
        if n1 == 0 and n2 > 0:
            # Each dest hole grows from zero at its own position
            matched_holes1 = [create_zero_hole(hole) for hole in holes2]
            matched_holes2 = holes2.copy()
            return matched_holes1, matched_holes2

        # Case 4: Both have holes - greedy matching
        if n1 == n2:
            # Equal counts - greedy pairing by nearest centroids
            return self._match_equal(holes1, holes2)
        elif n1 < n2:
            # Fewer source holes - duplicate them to match dest count
            return self._match_fewer_sources(holes1, holes2)
        else:  # n1 > n2
            # More source holes - multiple sources merge to single dest
            return self._match_more_sources(holes1, holes2)

    def _match_equal(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match holes when counts are equal using greedy nearest-centroid

        Uses greedy matching without replacement: each hole is used exactly once.
        """
        # Calculate centroids
        centroids1 = [hole.centroid() for hole in holes1]
        centroids2 = [hole.centroid() for hole in holes2]

        # Greedy matching: for each hole2, find nearest hole1
        matched_holes1 = []
        matched_holes2 = []
        used_indices = set()

        for i, c2 in enumerate(centroids2):
            # Find nearest unused hole1
            best_idx = None
            best_dist = float('inf')

            for j, c1 in enumerate(centroids1):
                if j in used_indices:
                    continue
                dist = math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j

            if best_idx is not None:
                used_indices.add(best_idx)
                matched_holes1.append(holes1[best_idx])
                matched_holes2.append(holes2[i])

        return matched_holes1, matched_holes2

    def _match_fewer_sources(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match when there are fewer source holes (holes splitting)

        Each dest hole is matched to its nearest source hole.
        Source holes may be used multiple times (splitting effect).
        """
        centroids1 = [hole.centroid() for hole in holes1]
        centroids2 = [hole.centroid() for hole in holes2]

        matched_holes1 = []
        matched_holes2 = []

        for c2, hole2 in zip(centroids2, holes2):
            # Find nearest source hole
            best_idx = 0
            best_dist = float('inf')

            for j, c1 in enumerate(centroids1):
                dist = math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j

            matched_holes1.append(holes1[best_idx])
            matched_holes2.append(hole2)

        return matched_holes1, matched_holes2

    def _match_more_sources(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match when there are more source holes (holes merging)

        Each source hole is matched to its nearest dest hole.
        Dest holes may be used multiple times (merging effect).
        """
        centroids1 = [hole.centroid() for hole in holes1]
        centroids2 = [hole.centroid() for hole in holes2]

        matched_holes1 = []
        matched_holes2 = []

        for c1, hole1 in zip(centroids1, holes1):
            # Find nearest dest hole
            best_idx = 0
            best_dist = float('inf')

            for j, c2 in enumerate(centroids2):
                dist = math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j

            matched_holes1.append(hole1)
            matched_holes2.append(holes2[best_idx])

        return matched_holes1, matched_holes2
