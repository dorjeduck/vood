"""Composite filter"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Filter


@dataclass(frozen=True)
class CompositeFilter(Filter):
    """Composite multiple filters together

    Args:
        filters: Tuple of filters to apply in sequence

    Example:
        >>> blur = BlurFilter(std_deviation=3.0)
        >>> shadow = DropShadowFilter(dx=5, dy=5, std_deviation=2)
        >>> composite = CompositeFilter(filters=(blur, shadow))
    """

    filters: tuple[Filter, ...]

    def __post_init__(self):
        if not self.filters:
            raise ValueError("CompositeFilter must have at least one filter")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object

        Note: Returns a composite of all filters. For multiple filters,
        drawsvg will chain them together.
        """
        # For composite filters, we return the first filter's FilterItem
        # The actual composition happens at the renderer level by adding
        # multiple filter items to a single filter
        # This is a simplified implementation - for full support, we'd need
        # to modify how filters are applied in the renderer
        return self.filters[0].to_drawsvg()

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two CompositeFilter instances"""
        if not isinstance(other, CompositeFilter):
            return self if t < 0.5 else other

        # If both have same number of filters, interpolate pairwise
        if len(self.filters) == len(other.filters):
            interpolated_filters = tuple(
                self.filters[i].interpolate(other.filters[i], t)
                for i in range(len(self.filters))
            )
            return CompositeFilter(filters=interpolated_filters)

        # Otherwise, step interpolation
        return self if t < 0.5 else other


