"""Discrete hole mapping strategy

This module provides a discrete hole transition strategy where holes don't merge
or split - instead they move, appear (grow from zero), or disappear (shrink to zero)
at their current positions.
"""

from __future__ import annotations
import math
from typing import List, Tuple

from vood.component.vertex import VertexLoop
from .base import HoleMapper
from .utils import create_zero_hole


class DiscreteMapper(HoleMapper):
    """Discrete hole transitions with selective matching

    This strategy creates discrete transitions where holes don't merge or split:
    - Some holes move to new positions (matched pairs)
    - Excess holes shrink to zero at their current positions
    - New holes grow from zero at their final positions

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
    - Mixed transitions (some holes move, others appear/disappear)
    - Balanced visual complexity
    """

    def __init__(self, selection_method: str = "distance"):
        """Initialize discrete matcher

        Args:
            selection_method: How to select which holes move vs. appear/disappear
                            Currently only "distance" is supported
        """
        self.selection_method = selection_method

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

        # Case 2: Source has holes, dest has none (all holes shrink to zero)
        if n1 > 0 and n2 == 0:
            matched_holes1 = holes1.copy()
            matched_holes2 = [create_zero_hole(hole) for hole in holes1]
            return matched_holes1, matched_holes2

        # Case 3: Source has no holes, dest has holes (all holes grow from zero)
        if n1 == 0 and n2 > 0:
            matched_holes1 = [create_zero_hole(hole) for hole in holes2]
            matched_holes2 = holes2.copy()
            return matched_holes1, matched_holes2

        # Case 4: Both have holes
        if n1 == n2:
            # Equal counts - standard optimal matching
            return self._match_equal(holes1, holes2)
        elif n1 > n2:
            # More sources - some shrink to zero in place
            return self._match_with_disappearance(holes1, holes2)
        else:  # n1 < n2
            # Fewer sources - some grow from zero
            return self._match_with_appearance(holes1, holes2)

    def _match_equal(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Optimal 1:1 matching for equal hole counts"""
        # Use greedy nearest-centroid matching
        centroids1 = [hole.centroid() for hole in holes1]
        centroids2 = [hole.centroid() for hole in holes2]

        matched_holes1 = []
        matched_holes2 = []
        used_indices = set()

        for i, c2 in enumerate(centroids2):
            best_idx = None
            best_dist = float('inf')

            for j, c1 in enumerate(centroids1):
                if j in used_indices:
                    continue
                dist = self._distance(c1, c2)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j

            if best_idx is not None:
                used_indices.add(best_idx)
                matched_holes1.append(holes1[best_idx])
                matched_holes2.append(holes2[i])

        return matched_holes1, matched_holes2

    def _match_with_disappearance(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match when N > M: some sources shrink to zero in place

        Strategy:
        1. Select M sources that are closest to the M destinations
        2. Match these M sources to M destinations optimally
        3. Remaining (N-M) sources shrink to zero at their positions
        """
        n1 = len(holes1)
        n2 = len(holes2)

        # Select M sources closest to destinations (these will move)
        selected_indices = self._select_closest_sources(holes1, holes2, n2)
        selected_sources = [holes1[i] for i in selected_indices]
        unselected_sources = [holes1[i] for i in range(n1) if i not in selected_indices]

        # Match selected sources to destinations optimally
        matched_sel1, matched_sel2 = self._match_equal(selected_sources, holes2)

        # Add unselected sources (shrink to zero in place)
        matched_holes1 = matched_sel1 + unselected_sources
        matched_holes2 = matched_sel2 + [create_zero_hole(h) for h in unselected_sources]

        return matched_holes1, matched_holes2

    def _match_with_appearance(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match when N < M: some destinations grow from zero

        Strategy:
        1. Select N destinations closest to the N sources
        2. Match N sources to these N destinations optimally
        3. Remaining (M-N) destinations grow from zero at their positions
        """
        n1 = len(holes1)
        n2 = len(holes2)

        # Select N destinations closest to sources (these will receive moving holes)
        selected_indices = self._select_closest_destinations(holes1, holes2, n1)
        selected_destinations = [holes2[i] for i in selected_indices]
        unselected_destinations = [holes2[i] for i in range(n2) if i not in selected_indices]

        # Match sources to selected destinations optimally
        matched_sel1, matched_sel2 = self._match_equal(holes1, selected_destinations)

        # Add unselected destinations (grow from zero)
        matched_holes1 = matched_sel1 + [create_zero_hole(h) for h in unselected_destinations]
        matched_holes2 = matched_sel2 + unselected_destinations

        return matched_holes1, matched_holes2

    def _select_closest_sources(
        self,
        sources: List[VertexLoop],
        destinations: List[VertexLoop],
        count: int
    ) -> List[int]:
        """Select 'count' sources that are collectively closest to destinations

        Uses a greedy approach: repeatedly select the source with minimum
        distance to any destination.
        """
        src_centroids = [hole.centroid() for hole in sources]
        dst_centroids = [hole.centroid() for hole in destinations]

        selected = []
        available = set(range(len(sources)))

        for _ in range(count):
            if not available:
                break

            # Find source with minimum distance to any destination
            best_idx = None
            best_dist = float('inf')

            for i in available:
                min_dist = min(self._distance(src_centroids[i], dst_c)
                             for dst_c in dst_centroids)
                if min_dist < best_dist:
                    best_dist = min_dist
                    best_idx = i

            if best_idx is not None:
                selected.append(best_idx)
                available.remove(best_idx)

        return selected

    def _select_closest_destinations(
        self,
        sources: List[VertexLoop],
        destinations: List[VertexLoop],
        count: int
    ) -> List[int]:
        """Select 'count' destinations that are collectively closest to sources

        Uses a greedy approach: repeatedly select the destination with minimum
        distance to any source.
        """
        src_centroids = [hole.centroid() for hole in sources]
        dst_centroids = [hole.centroid() for hole in destinations]

        selected = []
        available = set(range(len(destinations)))

        for _ in range(count):
            if not available:
                break

            # Find destination with minimum distance to any source
            best_idx = None
            best_dist = float('inf')

            for i in available:
                min_dist = min(self._distance(dst_centroids[i], src_c)
                             for src_c in src_centroids)
                if min_dist < best_dist:
                    best_dist = min_dist
                    best_idx = i

            if best_idx is not None:
                selected.append(best_idx)
                available.remove(best_idx)

        return selected

    def _distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Euclidean distance between two points"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
