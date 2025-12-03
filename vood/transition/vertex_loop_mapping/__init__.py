"""Hole mapping strategies for morph interpolation

This package provides pluggable strategies for mapping vertex loops between two states
during morphing. Different strategies handle varying hole counts (N→M) differently.

Available mappers:
- ClusteringMapper: Spatial k-means clustering for balanced grouping (default)
- GreedyNearestMapper: Fast greedy nearest-centroid matching
- HungarianMapper: Optimal assignment algorithm (requires scipy)
- DiscreteMapper: Discrete transitions with selective mapping (some move, some appear/disappear)
- SimpleMapper: All old vertex loops disappear, all new vertex loops appear (no mapping)

Utilities:
- create_zero_vertex_loop: Create zero-sized vertex loops for creation/destruction effects
"""

from .base import VertexLoopMapper
from .greedy import GreedyNearestMapper
from .clustering import ClusteringMapper
from .hungarian import HungarianMapper
from .discrete import DiscreteMapper
from .simple import SimpleMapper
from .utils import create_zero_vertex_loop

__all__ = [
    "VertexLoopMapper",
    "GreedyNearestMapper",
    "ClusteringMapper",
    "HungarianMapper",
    "DiscreteMapper",
    "SimpleMapper",
    "create_zero_vertex_loop",
]
