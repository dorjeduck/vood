"""Abstract base class for gradients"""

from __future__ import annotations
from abc import ABC, abstractmethod

import drawsvg as dw


class Gradient(ABC):
    """Abstract base class for gradient fills and strokes"""

    @abstractmethod
    def to_drawsvg(self) -> dw.LinearGradient | dw.RadialGradient:
        """Convert to drawsvg gradient object

        Returns:
            drawsvg gradient object ready to use as fill/stroke
        """
        pass

    @abstractmethod
    def interpolate(self, other: "Gradient", t: float) -> "Gradient":
        """Interpolate between this gradient and another gradient

        Args:
            other: Another Gradient object to interpolate with
            t: Interpolation factor (0 <= t <= 1), where 0 returns self and 1 returns other

        Returns:
            Interpolated Gradient object. For same-class gradients with matching stops,
            values are smoothly interpolated. Otherwise returns step interpolation
            (self if t < 0.5, else other).
        """
        pass
