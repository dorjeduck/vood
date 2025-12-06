"""Abstract base class for filters"""

from __future__ import annotations
from abc import ABC, abstractmethod

import drawsvg as dw



class Filter(ABC):
    """Abstract base class for SVG filter effects

    All filter subclasses must implement to_drawsvg() to convert
    to a drawsvg FilterItem object.
    """

    @abstractmethod
    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object

        Returns:
            drawsvg FilterItem object ready to use as filter
        """
        pass

    @abstractmethod
    def interpolate(self, other: "Filter", t: float) -> "Filter":
        """Interpolate between this filter and another filter

        Args:
            other: Another Filter object to interpolate with
            t: Interpolation factor (0 <= t <= 1), where 0 returns self and 1 returns other

        Returns:
            Interpolated Filter object. For same-class filters, values are smoothly
            interpolated. For different-class filters, returns step interpolation
            (self if t < 0.5, else other).
        """
        pass


