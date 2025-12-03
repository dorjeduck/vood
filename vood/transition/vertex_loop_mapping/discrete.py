"""Discrete vertex loop mapping strategy

This module provides a discrete vertex loop transition strategy where vertex loops don't merge
or split - instead they move, appear (grow from zero), or disappear (shrink to zero)
at their current positions.
"""

from __future__ import annotations
from typing import List, Tuple

from vood.component.vertex import VertexLoop
from .base import VertexLoopMapper
from .utils import create_zero_vertex_loop


class DiscreteMapper(VertexLoopMapper):
    """Discrete vertex loo transitions with selective matching

    This strategy creates discrete transitions where vertex loops don't merge or split:
    - Some vertex loops move to new positions (matched pairs)
    - Excess vertex loops shrink to zero at their current positions
    - New vertex loops grow from zero at their final positions

    Visual effect: Clean, discrete transitions rather than fluid merging/splitting.

    Algorithm:
    1. For N > M (fewer destinations):
       - Select M sources closest to destinations (these move)
       - Remaining (N-M) sources shrink to zero at their positions

    2. For N < M (more destinations):
       - Match N sources to N closest destinations (these move)
       - Remaining (M-N) destinations grow from zero at their positions

    3. For N = M:
       - Standard 1:1 optimal matching

    Use cases:
    - UI elements with discrete appearance/disappearance
    - When merging effect looks too busy or confusing
    - Mixed transitions (some vertex loops move, others appear/disappear)
    - Balanced visual complexity
    """

    def __init__(self, selection_method: str = "distance"):
        """Initialize discrete mapper

        Args:
            selection_method: How to select which vertex loops move vs. appear/disappear
                            Currently only "distance" is supported
        """
        self.selection_method = selection_method

    def map(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        n1 = len(vertex_loops1)
        n2 = len(vertex_loops2)

        # Case 1: No vertex loops on either side
        if n1 == 0 and n2 == 0:
            return [], []

        # Case 2: Source has  vertex_loops , dest has none (all vertex loops shrink to zero)
        if n1 > 0 and n2 == 0:
            matched_vertex_loops1 = vertex_loops1.copy()
            matched_vertex_loops2 = [
                create_zero_vertex_loop(vertex_loop) for vertex_loop in vertex_loops1
            ]
            return matched_vertex_loops1, matched_vertex_loops2

        # Case 3: Source has no  vertex_loops , dest has vertex loops (all vertex loops grow from zero)
        if n1 == 0 and n2 > 0:
            matched_vertex_loops1 = [
                create_zero_vertex_loop(vertex_loop) for vertex_loop in vertex_loops2
            ]
            matched_vertex_loops2 = vertex_loops2.copy()
            return matched_vertex_loops1, matched_vertex_loops2

        # Case 4: Both have  vertex_loops
        if n1 == n2:
            # Equal counts - standard optimal matching
            return self._match_equal(vertex_loops1, vertex_loops2)
        elif n1 > n2:
            # More sources - some shrink to zero in place
            return self._match_with_disappearance(vertex_loops1, vertex_loops2)
        else:  # n1 < n2
            # Fewer sources - some grow from zero
            return self._match_with_appearance(vertex_loops1, vertex_loops2)

    def _match_equal(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Optimal 1:1 matching for equal vertex loop counts"""
        # Use greedy nearest-centroid matching
        centroids1 = [vertex_loop.centroid() for vertex_loop in vertex_loops1]
        centroids2 = [vertex_loop.centroid() for vertex_loop in vertex_loops2]

        matched_vertex_loops1 = []
        matched_vertex_loops2 = []
        used_indices = set()

        for i, c2 in enumerate(centroids2):
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

    def _match_with_disappearance(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match when N > M: some sources shrink to zero in place

        Strategy:
        1. Select M sources that are closest to the M destinations
        2. Match these M sources to M destinations optimally
        3. Remaining (N-M) sources shrink to zero at their positions
        """
        n1 = len(vertex_loops1)
        n2 = len(vertex_loops2)

        # Select M sources closest to destinations (these will move)
        selected_indices = self._select_closest_sources(
            vertex_loops1, vertex_loops2, n2
        )
        selected_sources = [vertex_loops1[i] for i in selected_indices]
        unselected_sources = [
            vertex_loops1[i] for i in range(n1) if i not in selected_indices
        ]

        # Match selected sources to destinations optimally
        matched_sel1, matched_sel2 = self._match_equal(selected_sources, vertex_loops2)

        # Add unselected sources (shrink to zero in place)
        matched_vertex_loops1 = matched_sel1 + unselected_sources
        matched_vertex_loops2 = matched_sel2 + [
            create_zero_vertex_loop(h) for h in unselected_sources
        ]

        return matched_vertex_loops1, matched_vertex_loops2

    def _match_with_appearance(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match when N < M: some destinations grow from zero

        Strategy:
        1. Select N destinations closest to the N sources
        2. Match N sources to these N destinations optimally
        3. Remaining (M-N) destinations grow from zero at their positions
        """
        n1 = len(vertex_loops1)
        n2 = len(vertex_loops2)

        # Select N destinations closest to sources (these will receive moving  vertex_loops )
        selected_indices = self._select_closest_destinations(
            vertex_loops1, vertex_loops2, n1
        )
        selected_destinations = [vertex_loops2[i] for i in selected_indices]
        unselected_destinations = [
            vertex_loops2[i] for i in range(n2) if i not in selected_indices
        ]

        # Match sources to selected destinations optimally
        matched_sel1, matched_sel2 = self._match_equal(
            vertex_loops1, selected_destinations
        )

        # Add unselected destinations (grow from zero)
        matched_vertex_loops1 = matched_sel1 + [
            create_zero_vertex_loop(h) for h in unselected_destinations
        ]
        matched_vertex_loops2 = matched_sel2 + unselected_destinations

        return matched_vertex_loops1, matched_vertex_loops2

    def _select_closest_sources(
        self, sources: List[VertexLoop], destinations: List[VertexLoop], count: int
    ) -> List[int]:
        """Select 'count' sources that are collectively closest to destinations

        Uses a greedy approach: repeatedly select the source with minimum
        distance to any destination.
        """
        src_centroids = [vertex_loop.centroid() for vertex_loop in sources]
        dst_centroids = [vertex_loop.centroid() for vertex_loop in destinations]

        selected = []
        available = set(range(len(sources)))

        for _ in range(count):
            if not available:
                break

            # Find source with minimum distance to any destination
            best_idx = None
            best_dist = float("inf")

            for i in available:
                min_dist = min(
                    src_centroids[i].distance_to(dst_c) for dst_c in dst_centroids
                )
                if min_dist < best_dist:
                    best_dist = min_dist
                    best_idx = i

            if best_idx is not None:
                selected.append(best_idx)
                available.remove(best_idx)

        return selected

    def _select_closest_destinations(
        self, sources: List[VertexLoop], destinations: List[VertexLoop], count: int
    ) -> List[int]:
        """Select 'count' destinations that are collectively closest to sources

        Uses a greedy approach: repeatedly select the destination with minimum
        distance to any source.
        """
        src_centroids = [vertex_loop.centroid() for vertex_loop in sources]
        dst_centroids = [vertex_loop.centroid() for vertex_loop in destinations]

        selected = []
        available = set(range(len(destinations)))

        for _ in range(count):
            if not available:
                break

            # Find destination with minimum distance to any source
            best_idx = None
            best_dist = float("inf")

            for i in available:
                min_dist = min(
                    dst_centroids[i].distance_to(src_c) for src_c in src_centroids
                )
                if min_dist < best_dist:
                    best_dist = min_dist
                    best_idx = i

            if best_idx is not None:
                selected.append(best_idx)
                available.remove(best_idx)

        return selected
