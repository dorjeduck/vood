"""Simple hole mapping strategy

This module provides the simplest hole transition strategy: all old holes shrink
to zero at their positions, and all new holes grow from zero at their positions.
No matching or correspondence between old and new holes.
"""

from __future__ import annotations
from typing import List, Tuple

from vood.component.vertex import VertexLoop
from .base import HoleMapper
from .utils import create_zero_hole


class SimpleMapper(HoleMapper):
    """Simplest hole transitions - all old disappear, all new appear

    This strategy provides the most straightforward hole transitions:
    - ALL old holes shrink to zero at their current positions
    - ALL new holes grow from zero at their final positions
    - NO matching or movement between old and new holes
    - Complete independence between source and destination

    Visual effect: Clean crossfade-like transition where old holes fade out
    and new holes fade in, with no movement or spatial correspondence.

    Algorithm:
    - For any N → M transition:
      - All N source holes → zero-sized holes at source positions
      - All M destination holes ← zero-sized holes at destination positions
      - No selection, clustering, or matching logic

    Use cases:
    - Completely different hole layouts (matching would look awkward)
    - Clean slate transitions (old state exits, new state enters)
    - Simplest possible animation (no complex spatial logic)
    - When you want discrete "before/after" rather than continuous morphing

    Performance: O(N + M) - fastest possible strategy (just create zero-holes)
    """

    def map(
        self,
        holes1: List[VertexLoop],
        holes2: List[VertexLoop]
    ) -> Tuple[List[VertexLoop], List[VertexLoop]]:
        """Match holes with no correspondence - all disappear and appear

        Args:
            holes1: Source holes
            holes2: Destination holes

        Returns:
            Tuple of (matched_holes1, matched_holes2) where:
            - All source holes are paired with zero-holes (they shrink to zero)
            - All destination holes are paired with zero-holes (they grow from zero)
        """
        # Every source hole shrinks to zero at its position
        sources_to_zero = [create_zero_hole(hole) for hole in holes1]

        # Every destination hole grows from zero at its position
        destinations_from_zero = [create_zero_hole(hole) for hole in holes2]

        # Return paired lists: old holes + new holes
        matched_holes1 = holes1 + destinations_from_zero
        matched_holes2 = sources_to_zero + holes2

        return matched_holes1, matched_holes2
