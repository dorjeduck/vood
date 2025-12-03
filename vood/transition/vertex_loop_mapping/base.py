"""Base classes and interfaces for vertext loop mapping strategies

This module defines the abstract base class for all vertext loop mapping strategies
used during morph interpolation when shapes have different vertext loop counts.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple

from vood.component.vertex import VertexLoop


class VertexLoopMapper(ABC):
    """Abstract base for vertext loop mapping strategies

    Mapping strategies determine how to pair vertex_loops from two states when
    morphing between shapes with different vertext loop counts (N → M).

    Implementations must handle:
    - N = M: Equal vertext loop counts (1:1 mapping)
    - N > M: More source vertex_loops (merging)
    - N < M: Fewer source vertex_loops (splitting)
    - N = 0 or M = 0: vertext loop creation/destruction
    """

    @abstractmethod
    def map(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Map vertex_loops between two states

        Returns equal-length lists where mapped_vertex_loops1[i] from state1
        corresponds to mapped_vertex_loops2[i] from state2. May create zero-sized
        vertex_loops or duplicate vertex_loops to handle mismatched counts.

        Args:
            vertex_loops1: List of vertex_loops from first state
            vertex_loops2: List of vertex_loops from second state

        Returns:
            Tuple of (mapped_vertex_loops1, mapped_vertex_loops2) with equal lengths
        """
        pass
