"""Hungarian algorithm vertex_loop mapping strategy

This module provides optimal vertex_loop mapping using the Hungarian (Munkres)
algorithm for globally minimal centroid distance assignment.

Requires scipy for the linear_sum_assignment implementation.
"""

from __future__ import annotations
import math
from typing import List, Tuple

from vood.component.vertex import VertexLoop
from .base import VertexLoopMapper
from .utils import create_zero_vertex_loop

# Try to import scipy
try:
    from scipy.optimize import linear_sum_assignment

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class HungarianMapper(VertexLoopMapper):
    """Optimal  mapping using Hungarian algorithm

    Uses the Hungarian (Munkres) algorithm for globally optimal assignment.
    Minimizes total centroid distance across all pairings, unlike greedy
    matching which may get stuck in local minima.

    Algorithm:
    1. Build cost matrix of centroid distances between all vertex_loop pairs
    2. For N≠M cases, replicate vertex loops to create square matrix
    3. Apply Hungarian algorithm to find minimum-cost perfect matching
    4. Map assignments back to original  vertex_loops

    For N>M (merging): Replicates each destination M times to handle multiple sources
    For N<M (splitting): Replicates each source N times to handle multiple destinations
    For N=M: Direct optimal 1:1 assignment

    Advantages over greedy:
    - Globally optimal (minimum total distance)
    - Better results when vertex loops are clustered or evenly spaced
    - More predictable behavior

    Disadvantages:
    - Slower: O(n³) vs O(n²) for greedy
    - Requires scipy (optional dependency)

    Requires: scipy.optimize.linear_sum_assignment
    """

    def map(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        if not SCIPY_AVAILABLE:
            raise ImportError(
                "Hungarian mapper requires scipy. Install it with:\n"
                "  pip install scipy\n\n"
                "Or use a different mapper in vood.toml:\n"
                "  [morphing]\n"
                '  vertex_loop_mapper = "clustering"  # or "greedy"'
            )

        n1 = len(vertex_loops1)
        n2 = len(vertex_loops2)

        # Case 1: No vertex loops on either side
        if n1 == 0 and n2 == 0:
            return [], []

        # Case 2: Source has  vertex_loops , dest has none ( vertex_loops  disappear)
        if n1 > 0 and n2 == 0:
            matched_vertex_loops1 = vertex_loops1.copy()
            matched_vertex_loops2 = [create_zero_vertex_loop(vertex_loop) for vertex_loop in vertex_loops1]
            return matched_vertex_loops1, matched_vertex_loops2

        # Case 3: Source has no  vertex_loops , dest has vertex loops ( vertex_loops  appear)
        if n1 == 0 and n2 > 0:
            matched_vertex_loops1 = [create_zero_vertex_loop(vertex_loop) for vertex_loop in vertex_loops2]
            matched_vertex_loops2 = vertex_loops2.copy()
            return matched_vertex_loops1, matched_vertex_loops2

        # Case 4: Both have vertex loops - use Hungarian algorithm
        if n1 == n2:
            # Equal counts - standard Hungarian
            return self._match_equal(vertex_loops1, vertex_loops2)
        elif n1 < n2:
            # Fewer sources - replicate sources for splitting
            return self._match_with_replication(
                vertex_loops1, vertex_loops2, replicate_sources=True
            )
        else:  # n1 > n2
            # More sources - replicate destinations for merging
            return self._match_with_replication(
                vertex_loops1, vertex_loops2, replicate_sources=False
            )

    def _match_equal(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Hungarian matching for equal vertex_loop counts (N=M)"""
        n = len(vertex_loops1)

        # Build cost matrix (distances between centroids)
        cost_matrix = []
        centroids1 = [vertex_loop.centroid() for vertex_loop in vertex_loops1]
        centroids2 = [vertex_loop.centroid() for vertex_loop in vertex_loops2]

        for c1 in centroids1:
            row = []
            for c2 in centroids2:
                dist = c1.distance_to(c2)
                row.append(dist)
            cost_matrix.append(row)

        # Apply Hungarian algorithm
        row_indices, col_indices = linear_sum_assignment(cost_matrix)

        # Build matched pairs
        matched_vertex_loops1 = [vertex_loops1[i] for i in row_indices]
        matched_vertex_loops2 = [vertex_loops2[j] for j in col_indices]

        return matched_vertex_loops1, matched_vertex_loops2

    def _match_with_replication(
        self,
        vertex_loops1: List[VertexLoop],
        vertex_loops2: List[VertexLoop],
        replicate_sources: bool,
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Hungarian matching with replication for unequal counts (N≠M)

        Args:
            replicate_sources: If True, replicate vertex_loops1 (splitting case N<M)
                             If False, replicate vertex_loops2 (merging case N>M)
        """
        n1 = len(vertex_loops1)
        n2 = len(vertex_loops2)

        if replicate_sources:
            # N < M: Replicate each source to cover all destinations
            # Create cost matrix: M×M where sources are replicated
            centroids1 = [vertex_loop.centroid() for vertex_loop in vertex_loops1]
            centroids2 = [vertex_loop.centroid() for vertex_loop in vertex_loops2]

            # Build M×M cost matrix (replicate sources to size M)
            cost_matrix = []
            source_map = []  # Maps matrix row to original source index

            for _ in range(n2):  # Need M rows
                for i in range(n1):  # Replicate all sources
                    row = []
                    for c2 in centroids2:
                        dist = centroids1[i].distance_to(c2)
                        row.append(dist)
                    cost_matrix.append(row)
                    source_map.append(i)

            # Apply Hungarian (may use fewer rows than M×M due to replication)
            cost_matrix = cost_matrix[:n2]  # Trim to M×M
            source_map = source_map[:n2]

            row_indices, col_indices = linear_sum_assignment(cost_matrix)

            # Build matched pairs (sources may appear multiple times)
            matched_vertex_loops1 = [vertex_loops1[source_map[i]] for i in row_indices]
            matched_vertex_loops2 = [vertex_loops2[j] for j in col_indices]

            return matched_vertex_loops1, matched_vertex_loops2

        else:
            # N > M: Replicate each destination to cover all sources
            # Create cost matrix: N×N where destinations are replicated
            centroids1 = [vertex_loop.centroid() for vertex_loop in vertex_loops1]
            centroids2 = [vertex_loop.centroid() for vertex_loop in vertex_loops2]

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
                    dist = c1.distance_to(centroids2[j])
                    row.append(dist)
                cost_matrix.append(row)

            dest_map = dest_map[:n1]  # Trim to N

            row_indices, col_indices = linear_sum_assignment(cost_matrix)

            # Build matched pairs (destinations may appear multiple times)
            matched_vertex_loops1 = [vertex_loops1[i] for i in row_indices]
            matched_vertex_loops2 = [vertex_loops2[dest_map[j]] for j in col_indices]

            return matched_vertex_loops1, matched_vertex_loops2
