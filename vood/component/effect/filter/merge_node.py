"""Merge filter"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Filter


@dataclass(frozen=True)
class MergeNodeFilter(Filter):
    """Merge filter - composites multiple inputs

    Args:
        inputs: Tuple of input source names to merge

    Example:
        >>> merge = MergeNodeFilter(inputs=('SourceGraphic', 'blur1', 'blur2'))
    """

    inputs: tuple[str, ...]

    def __post_init__(self):
        if not self.inputs:
            raise ValueError("MergeNodeFilter must have at least one input")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        # feMerge requires feMergeNode children
        # This is a simplified implementation - drawsvg may need special handling
        merge = dw.FilterItem("feMerge")
        for input_name in self.inputs:
            node = dw.FilterItem("feMergeNode", in_=input_name)
            merge.append(node)
        return merge

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two MergeNodeFilter instances"""
        if not isinstance(other, MergeNodeFilter):
            return self if t < 0.5 else other

        # Step interpolation
        return self if t < 0.5 else other
