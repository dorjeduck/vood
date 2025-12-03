"""Greedy nearest-centroid vertex_loop mapping strategy

This module provides the default vertex_loop mapping implementation using a simple
greedy nearest-neighbor approach based on centroid distances.
"""

from __future__ import annotations
from typing import List, Tuple

from vood.component.vertex import VertexLoop
from .base import VertexLoopMapper
from .utils import create_zero_vertex_loop


class GreedyNearestMapper(VertexLoopMapper):
    """Match vertex loops using greedy nearest-centroid strategy

    Uses a simple greedy approach to match vertex loops based on centroid distances.
    This is fast (O(n²)) and works well for most cases.

    Handles different vertex loop counts:
    - N = M: Greedy 1:1 pairing by nearest centroids
    - N > M: Multiple sources merge to single dest (each source finds nearest dest)
    - N < M: Single source splits to multiple dests (each dest finds nearest source)
    - N = 0 or M = 0: vertex loops shrink/grow at their centroids

    Algorithm:
    - For equal counts: Greedy matching without replacement (each vertex loop used once)
    - For unequal counts: Greedy matching with replacement ( vertex_loops  can be reused)

    Note: This may not give globally optimal results. For better matching,
    consider HungarianMapper (when implemented).
    """

    def map(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        n1 = len(vertex_loops1)
        n2 = len(vertex_loops2)

        # Case 1: No vertex loops on either side
        if n1 == 0 and n2 == 0:
            return [], []

        # Case 2: Source has  vertex_loops , dest has none ( vertex_loops  disappear)
        if n1 > 0 and n2 == 0:
            # Each source vertex_loop shrinks to zero at its own position
            matched_vertex_loops1 = vertex_loops1.copy()
            matched_vertex_loops2 = [create_zero_vertex_loop(vertex_loop) for vertex_loop in vertex_loops1]
            return matched_vertex_loops1, matched_vertex_loops2

        # Case 3: Source has no  vertex_loops , dest has vertex loops ( vertex_loops  appear)
        if n1 == 0 and n2 > 0:
            # Each dest vertex_loop grows from zero at its own position
            matched_vertex_loops1 = [create_zero_vertex_loop(vertex_loop) for vertex_loop in vertex_loops2]
            matched_vertex_loops2 = vertex_loops2.copy()
            return matched_vertex_loops1, matched_vertex_loops2

        # Case 4: Both have vertex loops - greedy matching
        if n1 == n2:
            # Equal counts - greedy pairing by nearest centroids
            return self._match_equal(vertex_loops1, vertex_loops2)
        elif n1 < n2:
            # Fewer source vertex loops - duplicate them to match dest count
            return self._match_fewer_sources(vertex_loops1, vertex_loops2)
        else:  # n1 > n2
            # More source vertex loops - multiple sources merge to single dest
            return self._match_more_sources(vertex_loops1, vertex_loops2)

    def _match_equal(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match vertex loops when counts are equal using greedy nearest-centroid

        Uses greedy matching without replacement: each vertex_loop is used exactly once.
        """
        # Calculate centroids
        centroids1 = [vertex_loop.centroid() for vertex_loop in vertex_loops1]
        centroids2 = [vertex_loop.centroid() for vertex_loop in vertex_loops2]

        # Greedy matching: for each vertex_loop2, find nearest vertex_loop1
        matched_vertex_loops1 = []
        matched_vertex_loops2 = []
        used_indices = set()

        for i, c2 in enumerate(centroids2):
            # Find nearest unused vertex_loop1
            best_idx = None
            best_dist = float("inf")

            for j, c1 in enumerate(centroids1):
                if j in used_indices:
                    continue
                dist = c1.distance_to(c2)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j

            if best_idx is not None:
                used_indices.add(best_idx)
                matched_vertex_loops1.append(vertex_loops1[best_idx])
                matched_vertex_loops2.append(vertex_loops2[i])

        return matched_vertex_loops1, matched_vertex_loops2

    def _match_fewer_sources(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match when there are fewer source vertex loops ( vertex_loops  splitting)

        Each dest vertex_loop is matched to its nearest source vertex_loop.
        Source vertex loops may be used multiple times (splitting effect).
        """
        centroids1 = [vertex_loop.centroid() for vertex_loop in vertex_loops1]
        centroids2 = [vertex_loop.centroid() for vertex_loop in vertex_loops2]

        matched_vertex_loops1 = []
        matched_vertex_loops2 = []

        for c2, vertex_loop2 in zip(centroids2, vertex_loops2):
            # Find nearest source vertex_loop
            best_idx = 0
            best_dist = float("inf")

            for j, c1 in enumerate(centroids1):
                dist = c1.distance_to(c2)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j

            matched_vertex_loops1.append(vertex_loops1[best_idx])
            matched_vertex_loops2.append(vertex_loop2)

        return matched_vertex_loops1, matched_vertex_loops2

    def _match_more_sources(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match when there are more source vertex loops ( vertex_loops  merging)

        Each source vertex_loop is matched to its nearest dest vertex_loop.
        Dest vertex loops may be used multiple times (merging effect).
        """
        centroids1 = [vertex_loop.centroid() for vertex_loop in vertex_loops1]
        centroids2 = [vertex_loop.centroid() for vertex_loop in vertex_loops2]

        matched_vertex_loops1 = []
        matched_vertex_loops2 = []

        for c1, vertex_loop1 in zip(centroids1, vertex_loops1):
            # Find nearest dest vertex_loop
            best_idx = 0
            best_dist = float("inf")

            for j, c2 in enumerate(centroids2):
                dist = c1.distance_to(c2)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j

            matched_vertex_loops1.append(vertex_loop1)
            matched_vertex_loops2.append(vertex_loops2[best_idx])

        return matched_vertex_loops1, matched_vertex_loops2
