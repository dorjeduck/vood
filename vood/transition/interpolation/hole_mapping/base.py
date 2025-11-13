"""Base classes and interfaces for hole mapping strategies

This module defines the abstract base class for all hole mapping strategies
used during morph interpolation when shapes have different hole counts.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple

from vood.component.vertex import VertexLoop


class HoleMapper(ABC):
    """Abstract base for hole mapping strategies

    Mapping strategies determine how to pair holes from two states when
    morphing between shapes with different hole counts (N → M).

    Implementations must handle:
    - N = M: Equal hole counts (1:1 mapping)
    - N > M: More source holes (merging)
    - N < M: Fewer source holes (splitting)
    - N = 0 or M = 0: Hole creation/destruction
    """

    @abstractmethod
    def map(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Map holes between two states

        Returns equal-length lists where mapped_holes1[i] from state1
        corresponds to mapped_holes2[i] from state2. May create zero-sized
        holes or duplicate holes to handle mismatched counts.

        Args:
            holes1: List of holes from first state
            holes2: List of holes from second state

        Returns:
            Tuple of (mapped_holes1, mapped_holes2) with equal lengths
        """
        pass
