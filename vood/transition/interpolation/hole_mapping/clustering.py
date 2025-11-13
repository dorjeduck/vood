"""Clustering-based hole mapping strategy

This module provides a sophisticated hole mapping approach using
spatial clustering (k-means) for better N≠M hole grouping.
"""

from __future__ import annotations
import math
import random
from typing import List, Tuple

from vood.component.vertex import VertexLoop
from .base import HoleMapper
from .utils import create_zero_hole


class ClusteringMapper(HoleMapper):
    """Match holes using k-means clustering

    Uses spatial clustering to group N sources into M clusters when N≠M.
    More sophisticated than greedy matching, ensures spatially close holes
    merge/split together in a balanced way.

    Algorithm:
    1. For N > M (merging, e.g., 5→2):
       - Cluster N source holes into M groups using k-means
       - Match each cluster centroid to nearest destination hole
       - All holes in a cluster converge to the same destination

    2. For N < M (splitting, e.g., 2→5):
       - Cluster M destination holes into N groups
       - Match each source hole to nearest cluster centroid
       - Source hole splits into multiple destinations from the cluster

    3. For N = M:
       - Fall back to greedy nearest-centroid matching
    """

    def __init__(self, max_iterations: int = 50, random_seed: int = 42, balance_clusters: bool = True):
        """Initialize clustering matcher

        Args:
            max_iterations: Maximum k-means iterations
            random_seed: Random seed for reproducible clustering
            balance_clusters: If True, rebalance clusters after k-means to avoid extreme imbalances
        """
        self.max_iterations = max_iterations
        self.random_seed = random_seed
        self.balance_clusters = balance_clusters

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
            matched_holes1 = holes1.copy()
            matched_holes2 = [create_zero_hole(hole) for hole in holes1]
            return matched_holes1, matched_holes2

        # Case 3: Source has no holes, dest has holes (holes appear)
        if n1 == 0 and n2 > 0:
            matched_holes1 = [create_zero_hole(hole) for hole in holes2]
            matched_holes2 = holes2.copy()
            return matched_holes1, matched_holes2

        # Case 4: Both have holes
        if n1 == n2:
            # Equal counts - use greedy matching
            return self._match_equal_greedy(holes1, holes2)
        elif n1 > n2:
            # More sources - cluster sources into dest count groups (merging)
            return self._match_with_clustering(holes1, holes2, cluster_sources=True)
        else:  # n1 < n2
            # Fewer sources - cluster dests into source count groups (splitting)
            return self._match_with_clustering(holes1, holes2, cluster_sources=False)

    def _match_equal_greedy(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Greedy matching for equal hole counts"""
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

    def _match_with_clustering(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop],
        cluster_sources: bool
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match holes using bidirectional k-means clustering

        Uses improved hybrid approach: clusters BOTH sources and destinations,
        then matches cluster-to-cluster before mapping holes within matched clusters.

        Args:
            cluster_sources: If True, N > M (merging case)
                           If False, N < M (splitting case)
        """
        if cluster_sources:
            # N > M (merging): Use old single-side clustering approach
            # This case works well - don't change it
            return self._match_with_merging(holes1, holes2)
        else:
            # N < M (splitting): Use new bidirectional clustering
            return self._match_with_splitting(holes1, holes2)

    def _match_with_merging(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match holes for merging case (N > M) using single-side clustering"""
        # N > M: Cluster N sources into M groups, merge to M dests
        k = len(holes2)
        centroids = [hole.centroid() for hole in holes1]
        clusters = self._kmeans(centroids, k)

        # Balance clusters if requested
        if self.balance_clusters:
            clusters = self._balance_clusters(centroids, clusters, k)

        # Compute cluster centroids
        cluster_centroids = []
        cluster_hole_lists = []

        for cluster_idx in range(k):
            cluster_holes = [holes1[i] for i, c in enumerate(clusters) if c == cluster_idx]
            if cluster_holes:
                cluster_centroid = self._compute_centroid([holes1[i].centroid()
                                                          for i, c in enumerate(clusters)
                                                          if c == cluster_idx])
                cluster_centroids.append((cluster_idx, cluster_centroid))
                cluster_hole_lists.append(cluster_holes)

        # Match clusters to destinations using greedy algorithm with "used" tracking
        # This ensures each destination gets exactly one cluster (1:1 mapping)
        dest_centroids = [hole.centroid() for hole in holes2]
        used_dests = set()
        matched_holes1 = []
        matched_holes2 = []

        for cluster_idx, cluster_centroid in cluster_centroids:
            # Find nearest UNUSED destination
            best_dest_idx = None
            best_dist = float('inf')

            for j, dest_c in enumerate(dest_centroids):
                if j in used_dests:
                    continue

                dist = self._distance(cluster_centroid, dest_c)
                if dist < best_dist:
                    best_dist = dist
                    best_dest_idx = j

            if best_dest_idx is None:
                # All destinations used, skip this cluster (shouldn't happen with k=len(holes2))
                continue

            # Mark destination as used
            used_dests.add(best_dest_idx)

            # All holes in this cluster merge to the same destination
            cluster_holes = cluster_hole_lists[cluster_centroids.index((cluster_idx, cluster_centroid))]
            for hole in cluster_holes:
                matched_holes1.append(hole)
                matched_holes2.append(holes2[best_dest_idx])

        return matched_holes1, matched_holes2

    def _match_with_splitting(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match holes for splitting case (N < M) using spatial-aware bidirectional clustering

        For now, use simpler greedy approach with duplication for splitting.
        TODO: Implement true bidirectional spatial clustering.
        """
        # Fall back to simpler greedy approach for splitting
        # This avoids complex k-means issues with spatial separation
        return self._match_with_simple_splitting(holes1, holes2)

    def _match_with_simple_splitting(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Simple greedy splitting: each destination gets nearest source

        This is similar to GreedyNearestMapper but designed for splitting case.
        Each destination finds its nearest source (sources can be reused).
        """
        src_centroids = [hole.centroid() for hole in holes1]
        dst_centroids = [hole.centroid() for hole in holes2]

        matched_holes1 = []
        matched_holes2 = []

        # For each destination, find nearest source
        for dst_idx, dst_c in enumerate(dst_centroids):
            best_src_idx = 0
            best_dist = float('inf')

            for src_idx, src_c in enumerate(src_centroids):
                dist = self._distance(src_c, dst_c)
                if dist < best_dist:
                    best_dist = dist
                    best_src_idx = src_idx

            matched_holes1.append(holes1[best_src_idx])
            matched_holes2.append(holes2[dst_idx])

        return matched_holes1, matched_holes2

    def _match_with_splitting_DISABLED(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """DISABLED: Complex bidirectional clustering (has k-means alignment issues)

        Clusters both sources and destinations, matches cluster-to-cluster,
        then maps holes within each matched cluster pair.
        """
        n1 = len(holes1)
        n2 = len(holes2)

        # Determine number of clusters (use min of counts)
        k = min(n1, n2)

        src_centroids = [hole.centroid() for hole in holes1]
        dst_centroids = [hole.centroid() for hole in holes2]

        src_clusters = self._kmeans(src_centroids, k)
        dst_clusters = self._kmeans(dst_centroids, k)

        # Balance clusters if requested
        if self.balance_clusters:
            src_clusters = self._balance_clusters(src_centroids, src_clusters, k)
            dst_clusters = self._balance_clusters(dst_centroids, dst_clusters, k)

        # Compute cluster centroids
        src_cluster_centroids = []
        dst_cluster_centroids = []

        for i in range(k):
            src_points = [src_centroids[j] for j, c in enumerate(src_clusters) if c == i]
            dst_points = [dst_centroids[j] for j, c in enumerate(dst_clusters) if c == i]

            src_cluster_centroids.append(self._compute_centroid(src_points) if src_points else (0, 0))
            dst_cluster_centroids.append(self._compute_centroid(dst_points) if dst_points else (0, 0))

        # Match source clusters to destination clusters (cluster-to-cluster pairing)
        cluster_pairs = self._match_cluster_pairs(src_cluster_centroids, dst_cluster_centroids)

        # Map holes within each matched cluster pair
        matched_holes1 = []
        matched_holes2 = []

        for src_cluster_idx, dst_cluster_idx in cluster_pairs:
            # Get holes in each cluster
            src_cluster_holes = [holes1[i] for i, c in enumerate(src_clusters) if c == src_cluster_idx]
            dst_cluster_holes = [holes2[i] for i, c in enumerate(dst_clusters) if c == dst_cluster_idx]

            # Map holes within this cluster pair
            paired1, paired2 = self._map_within_cluster_pair(src_cluster_holes, dst_cluster_holes)

            matched_holes1.extend(paired1)
            matched_holes2.extend(paired2)

        return matched_holes1, matched_holes2

    def _match_cluster_pairs(
        self,
        src_cluster_centroids: List[Tuple[float, float]],
        dst_cluster_centroids: List[Tuple[float, float]]
    ) -> List[Tuple[int, int]]:
        """Match source clusters to destination clusters using greedy nearest pairing

        Args:
            src_cluster_centroids: Centroids of source clusters
            dst_cluster_centroids: Centroids of destination clusters

        Returns:
            List of (src_cluster_idx, dst_cluster_idx) pairs
        """
        k = len(src_cluster_centroids)
        pairs = []
        used_dst = set()

        # Greedy matching: for each source cluster, find nearest unused destination cluster
        for src_idx in range(k):
            best_dst_idx = None
            best_dist = float('inf')

            for dst_idx in range(len(dst_cluster_centroids)):
                if dst_idx in used_dst:
                    continue

                dist = self._distance(src_cluster_centroids[src_idx], dst_cluster_centroids[dst_idx])
                if dist < best_dist:
                    best_dist = dist
                    best_dst_idx = dst_idx

            if best_dst_idx is not None:
                pairs.append((src_idx, best_dst_idx))
                used_dst.add(best_dst_idx)

        return pairs

    def _map_within_cluster_pair(
        self,
        src_holes: List[VertexLoop],
        dst_holes: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Map holes within a matched source-destination cluster pair

        Handles the local N→M mapping within a single cluster:
        - If N = M: Use greedy nearest matching
        - If N > M: Merge (N sources → M destinations)
        - If N < M: Split/create (N sources → M destinations with zero-holes)

        Args:
            src_holes: Source holes in this cluster
            dst_holes: Destination holes in this cluster

        Returns:
            Tuple of (matched_src_holes, matched_dst_holes)
        """
        n_src = len(src_holes)
        n_dst = len(dst_holes)

        if n_src == 0 and n_dst == 0:
            return [], []

        if n_src == 0:
            # No sources - create zero-holes for all destinations
            return [create_zero_hole(h) for h in dst_holes], dst_holes

        if n_dst == 0:
            # No destinations - shrink all sources to zero
            return src_holes, [create_zero_hole(h) for h in src_holes]

        if n_src == n_dst:
            # Equal count - use greedy matching
            return self._match_equal_greedy(src_holes, dst_holes)

        elif n_src > n_dst:
            # More sources - merge (reuse each destination for closest sources)
            src_centroids = [h.centroid() for h in src_holes]
            dst_centroids = [h.centroid() for h in dst_holes]

            matched_src = []
            matched_dst = []

            # For each source, find nearest destination
            for i, src_c in enumerate(src_centroids):
                best_dst_idx = 0
                best_dist = float('inf')
                for j, dst_c in enumerate(dst_centroids):
                    dist = self._distance(src_c, dst_c)
                    if dist < best_dist:
                        best_dist = dist
                        best_dst_idx = j

                matched_src.append(src_holes[i])
                matched_dst.append(dst_holes[best_dst_idx])

            return matched_src, matched_dst

        else:  # n_src < n_dst
            # Fewer sources - split (reuse each source for closest destinations)
            src_centroids = [h.centroid() for h in src_holes]
            dst_centroids = [h.centroid() for h in dst_holes]

            matched_src = []
            matched_dst = []

            # For each destination, find nearest source
            for i, dst_c in enumerate(dst_centroids):
                best_src_idx = 0
                best_dist = float('inf')
                for j, src_c in enumerate(src_centroids):
                    dist = self._distance(dst_c, src_c)
                    if dist < best_dist:
                        best_dist = dist
                        best_src_idx = j

                matched_src.append(src_holes[best_src_idx])
                matched_dst.append(dst_holes[i])

            return matched_src, matched_dst

    def _balance_clusters(
        self,
        points: List[Tuple[float, float]],
        clusters: List[int],
        k: int
    ) -> List[int]:
        """Rebalance clusters to avoid extreme size imbalances

        After k-means, clusters may be very unbalanced (e.g., 4-1 split for 5 points).
        This method reassigns points to create more balanced clusters.

        Strategy: Move points from oversized clusters to undersized clusters,
        choosing points that are closest to the target cluster centroid.

        Args:
            points: Original points that were clustered
            clusters: Current cluster assignments from k-means
            k: Number of clusters

        Returns:
            Rebalanced cluster assignments
        """
        n = len(points)
        if n <= k:
            return clusters

        # Calculate cluster sizes
        cluster_sizes = [clusters.count(i) for i in range(k)]

        # Calculate ideal size and acceptable deviation
        ideal_size = n / k
        max_deviation = max(1, ideal_size * 0.4)  # Allow 40% deviation from ideal

        # Compute cluster centroids
        cluster_centroids = []
        for i in range(k):
            cluster_points = [points[j] for j, c in enumerate(clusters) if c == i]
            if cluster_points:
                cluster_centroids.append(self._compute_centroid(cluster_points))
            else:
                cluster_centroids.append((0.0, 0.0))

        # Rebalance: move points from large clusters to small clusters
        clusters = clusters.copy()  # Don't modify original
        max_iterations = n  # Safety limit

        for _ in range(max_iterations):
            cluster_sizes = [clusters.count(i) for i in range(k)]

            # Find most oversized and most undersized clusters
            max_cluster = max(range(k), key=lambda i: cluster_sizes[i])
            min_cluster = min(range(k), key=lambda i: cluster_sizes[i])

            max_size = cluster_sizes[max_cluster]
            min_size = cluster_sizes[min_cluster]

            # Check if balanced enough
            if max_size - min_size <= 1:
                break  # Balanced (within 1 point difference)

            # Don't rebalance if deviation is acceptable
            if abs(max_size - ideal_size) <= max_deviation and abs(min_size - ideal_size) <= max_deviation:
                break

            # Find point in max_cluster that is closest to min_cluster centroid
            candidates = [(j, points[j]) for j, c in enumerate(clusters) if c == max_cluster]
            if not candidates:
                break

            # Choose candidate closest to target cluster
            best_idx = min(candidates,
                          key=lambda x: self._distance(x[1], cluster_centroids[min_cluster]))[0]

            # Reassign point
            clusters[best_idx] = min_cluster

        return clusters

    def _kmeans(self, points: List[Tuple[float, float]], k: int) -> List[int]:
        """Simple k-means clustering implementation

        Args:
            points: List of (x, y) coordinates
            k: Number of clusters

        Returns:
            List of cluster assignments (one per point)
        """
        if k >= len(points):
            # More clusters than points - each point is its own cluster
            return list(range(len(points)))

        # Initialize: use k-means++ for better initial centroids
        random.seed(self.random_seed)
        centroids = self._kmeans_plusplus_init(points, k)

        # Iterate until convergence or max iterations
        for _ in range(self.max_iterations):
            # Assign points to nearest centroid
            clusters = []
            for point in points:
                best_cluster = 0
                best_dist = float('inf')
                for i, centroid in enumerate(centroids):
                    dist = self._distance(point, centroid)
                    if dist < best_dist:
                        best_dist = dist
                        best_cluster = i
                clusters.append(best_cluster)

            # Recompute centroids
            new_centroids = []
            for i in range(k):
                cluster_points = [points[j] for j, c in enumerate(clusters) if c == i]
                if cluster_points:
                    new_centroids.append(self._compute_centroid(cluster_points))
                else:
                    # Empty cluster - keep old centroid
                    new_centroids.append(centroids[i])

            # Check convergence
            if self._centroids_equal(centroids, new_centroids):
                break

            centroids = new_centroids

        return clusters

    def _kmeans_plusplus_init(
        self,
        points: List[Tuple[float, float]],
        k: int
    ) -> List[Tuple[float, float]]:
        """Initialize centroids using k-means++ algorithm"""
        centroids = [random.choice(points)]

        for _ in range(k - 1):
            # Compute distances to nearest existing centroid
            distances = []
            for point in points:
                min_dist = min(self._distance(point, c) for c in centroids)
                distances.append(min_dist ** 2)  # Square for probability weighting

            # Choose next centroid with probability proportional to distance²
            total_dist = sum(distances)
            if total_dist == 0:
                # All points are already centroids
                centroids.append(random.choice(points))
            else:
                r = random.uniform(0, total_dist)
                cumsum = 0
                for i, d in enumerate(distances):
                    cumsum += d
                    if cumsum >= r:
                        centroids.append(points[i])
                        break

        return centroids

    def _distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Euclidean distance between two points"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def _compute_centroid(self, points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Compute centroid of a set of points"""
        if not points:
            return (0.0, 0.0)
        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        return (x, y)

    def _centroids_equal(
        self,
        c1: List[Tuple[float, float]],
        c2: List[Tuple[float, float]],
        epsilon: float = 1e-6
    ) -> bool:
        """Check if two sets of centroids are equal within epsilon"""
        if len(c1) != len(c2):
            return False
        for (x1, y1), (x2, y2) in zip(c1, c2):
            if abs(x1 - x2) > epsilon or abs(y1 - y2) > epsilon:
                return False
        return True
