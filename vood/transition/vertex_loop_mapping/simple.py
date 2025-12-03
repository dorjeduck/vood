"""Simple vertex_loop mapping strategy

This module provides the simplest vertex_loop transition strategy: all old vertex loops shrink
to zero at their positions, and all new vertex loops grow from zero at their positions.
No matching or correspondence between old and new  vertex_loops .
"""

from __future__ import annotations
from typing import List, Tuple

from vood.component.vertex import VertexLoop
from .base import VertexLoopMapper
from .utils import create_zero_vertex_loop


class SimpleMapper(VertexLoopMapper):
    """Simplest vertex_loop transitions - all old disappear, all new appear

    This strategy provides the most straightforward vertex_loop transitions:
    - ALL old vertex loops shrink to zero at their current positions
    - ALL new vertex loops grow from zero at their final positions
    - NO matching or movement between old and new  vertex_loops
    - Complete independence between source and destination

    Visual effect: Clean crossfade-like transition where old vertex loops fade out
    and new vertex loops fade in, with no movement or spatial correspondence.

    Algorithm:
    - For any N → M transition:
      - All N source vertex loops → zero-sized vertex loops at source positions
      - All M destination vertex loops ← zero-sized vertex loops at destination positions
      - No selection, clustering, or matching logic

    Use cases:
    - Completely different vertex_loop layouts (matching would look awkward)
    - Clean slate transitions (old state exits, new state enters)
    - Simplest possible animation (no complex spatial logic)
    - When you want discrete "before/after" rather than continuous morphing

    Performance: O(N + M) - fastest possible strategy (just create zero- vertex_loops )
    """

    def map(
        self, vertex_loops1: List[VertexLoop], vertex_loops2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match vertex loops with no correspondence - all disappear and appear

        Args:
            vertex_loops1: Source  vertex_loops
            vertex_loops2: Destination  vertex_loops

        Returns:
            Tuple of (matched_vertex_loops1, matched_vertex_loops2) where:
            - All source vertex loops are paired with zero- vertex_loops  (they shrink to zero)
            - All destination vertex loops are paired with zero- vertex_loops  (they grow from zero)
        """
        # Every source vertex_loop shrinks to zero at its position
        sources_to_zero = [
            create_zero_vertex_loop(vertex_loop) for vertex_loop in vertex_loops1
        ]

        # Every destination vertex_loop grows from zero at its position
        destinations_from_zero = [
            create_zero_vertex_loop(vertex_loop) for vertex_loop in vertex_loops2
        ]

        # Return paired lists: old vertex loops + new  vertex_loops
        matched_vertex_loops1 = vertex_loops1 + destinations_from_zero
        matched_vertex_loops2 = sources_to_zero + vertex_loops2

        return matched_vertex_loops1, matched_vertex_loops2
