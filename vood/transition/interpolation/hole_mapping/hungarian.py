"""Hungarian algorithm hole mapping strategy

This module provides optimal hole mapping using the Hungarian (Munkres)
algorithm for globally minimal centroid distance assignment.

Requires scipy for the linear_sum_assignment implementation.
"""

from __future__ import annotations
import math
from typing import List, Tuple

from vood.component.vertex import VertexLoop
from .base import HoleMapper
from .utils import create_zero_hole

# Try to import scipy
try:
    from scipy.optimize import linear_sum_assignment
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class HungarianMapper(HoleMapper):
    """Optimal hole mapping using Hungarian algorithm

    Uses the Hungarian (Munkres) algorithm for globally optimal assignment.
    Minimizes total centroid distance across all pairings, unlike greedy
    matching which may get stuck in local minima.

    Algorithm:
    1. Build cost matrix of centroid distances between all hole pairs
    2. For N≠M cases, replicate holes to create square matrix
    3. Apply Hungarian algorithm to find minimum-cost perfect matching
    4. Map assignments back to original holes

    For N>M (merging): Replicates each destination M times to handle multiple sources
    For N<M (splitting): Replicates each source N times to handle multiple destinations
    For N=M: Direct optimal 1:1 assignment

    Advantages over greedy:
    - Globally optimal (minimum total distance)
    - Better results when holes are clustered or evenly spaced
    - More predictable behavior

    Disadvantages:
    - Slower: O(n³) vs O(n²) for greedy
    - Requires scipy (optional dependency)

    Requires: scipy.optimize.linear_sum_assignment
    """

    def map(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        if not SCIPY_AVAILABLE:
            raise ImportError(
                "Hungarian matcher requires scipy. Install it with:\n"
                "  pip install scipy\n\n"
                "Or use a different matcher in vood.toml:\n"
                "  [morphing]\n"
                "  hole_matcher = \"clustering\"  # or \"greedy\""
            )

        n1 = len(holes1)
        n2 = len(holes2)

        # Case 1: No holes on either side
        if n1 == 0 and n2 == 0:
            return [], []

        # Case 2: Source has holes, dest has none (holes disappear)
        if n1 > 0 and n2 == 0:
            matched_holes1 = holes1.copy()
            matched_holes2 = [create_zero_hole(hole) for hole in holes1]
            return matched_holes1, matched_holes2

        # Case 3: Source has no holes, dest has holes (holes appear)
        if n1 == 0 and n2 > 0:
            matched_holes1 = [create_zero_hole(hole) for hole in holes2]
            matched_holes2 = holes2.copy()
            return matched_holes1, matched_holes2

        # Case 4: Both have holes - use Hungarian algorithm
        if n1 == n2:
            # Equal counts - standard Hungarian
            return self._match_equal(holes1, holes2)
        elif n1 < n2:
            # Fewer sources - replicate sources for splitting
            return self._match_with_replication(holes1, holes2, replicate_sources=True)
        else:  # n1 > n2
            # More sources - replicate destinations for merging
            return self._match_with_replication(holes1, holes2, replicate_sources=False)

    def _match_equal(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Hungarian matching for equal hole counts (N=M)"""
        n = len(holes1)

        # Build cost matrix (distances between centroids)
        cost_matrix = []
        centroids1 = [hole.centroid() for hole in holes1]
        centroids2 = [hole.centroid() for hole in holes2]

        for c1 in centroids1:
            row = []
            for c2 in centroids2:
                dist = self._distance(c1, c2)
                row.append(dist)
            cost_matrix.append(row)

        # Apply Hungarian algorithm
        row_indices, col_indices = linear_sum_assignment(cost_matrix)

        # Build matched pairs
        matched_holes1 = [holes1[i] for i in row_indices]
        matched_holes2 = [holes2[j] for j in col_indices]

        return matched_holes1, matched_holes2

    def _match_with_replication(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop],
        replicate_sources: bool
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Hungarian matching with replication for unequal counts (N≠M)

        Args:
            replicate_sources: If True, replicate holes1 (splitting case N<M)
                             If False, replicate holes2 (merging case N>M)
        """
        n1 = len(holes1)
        n2 = len(holes2)

        if replicate_sources:
            # N < M: Replicate each source to cover all destinations
            # Create cost matrix: M×M where sources are replicated
            centroids1 = [hole.centroid() for hole in holes1]
            centroids2 = [hole.centroid() for hole in holes2]

            # Build M×M cost matrix (replicate sources to size M)
            cost_matrix = []
            source_map = []  # Maps matrix row to original source index

            for _ in range(n2):  # Need M rows
                for i in range(n1):  # Replicate all sources
                    row = []
                    for c2 in centroids2:
                        dist = self._distance(centroids1[i], c2)
                        row.append(dist)
                    cost_matrix.append(row)
                    source_map.append(i)

            # Apply Hungarian (may use fewer rows than M×M due to replication)
            cost_matrix = cost_matrix[:n2]  # Trim to M×M
            source_map = source_map[:n2]

            row_indices, col_indices = linear_sum_assignment(cost_matrix)

            # Build matched pairs (sources may appear multiple times)
            matched_holes1 = [holes1[source_map[i]] for i in row_indices]
            matched_holes2 = [holes2[j] for j in col_indices]

            return matched_holes1, matched_holes2

        else:
            # N > M: Replicate each destination to cover all sources
            # Create cost matrix: N×N where destinations are replicated
            centroids1 = [hole.centroid() for hole in holes1]
            centroids2 = [hole.centroid() for hole in holes2]

            # Build N×N cost matrix (replicate destinations to size N)
            dest_map = []  # Maps matrix column to original dest index

            for _ in range(n1):  # Need N columns
                for j in range(n2):  # Replicate all destinations
                    dest_map.append(j)

            # Build cost matrix
            cost_matrix = []
            for c1 in centroids1:
                row = []
                for j in dest_map[:n1]:  # Use first N replicated destinations
                    dist = self._distance(c1, centroids2[j])
                    row.append(dist)
                cost_matrix.append(row)

            dest_map = dest_map[:n1]  # Trim to N

            row_indices, col_indices = linear_sum_assignment(cost_matrix)

            # Build matched pairs (destinations may appear multiple times)
            matched_holes1 = [holes1[i] for i in row_indices]
            matched_holes2 = [holes2[dest_map[j]] for j in col_indices]

            return matched_holes1, matched_holes2

    def _distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Euclidean distance between two points"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
