"""Vertex alignment strategies for morph interpolation

This package provides pluggable strategies for aligning vertex lists during
morphing. Different strategies are used based on whether shapes are open/closed.

Available aligners:
- AngularAligner: For closed ↔ closed shapes (centroid-based)
- EuclideanAligner: For open ↔ closed shapes (distance-based)
- NullAligner: For open ↔ open shapes (no alignment)

Factory function:
- get_aligner(closed1, closed2): Auto-selects appropriate aligner
"""

from .base import VertexAligner, AlignmentContext, get_aligner
from .angular import AngularAligner
from .euclidean import EuclideanAligner
from .null import NullAligner

__all__ = [
    'VertexAligner',
    'AlignmentContext',
    'get_aligner',
    'AngularAligner',
    'EuclideanAligner',
    'NullAligner',
]
