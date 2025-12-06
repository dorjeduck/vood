"""Abstract base class for patterns"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw


@dataclass(frozen=True)
class Pattern(ABC):
    """Abstract base class for SVG pattern fills

    All pattern subclasses must implement to_drawsvg() to convert
    to a drawsvg Pattern object.
    """

    @abstractmethod
    def to_drawsvg(self, drawing: Optional[dw.Drawing] = None) -> dw.Pattern:
        """Convert to drawsvg Pattern object

        Args:
            drawing: Optional drawing for nested defs (clips, masks, etc.)

        Returns:
            drawsvg Pattern object ready to use as fill/stroke
        """
        pass

    @abstractmethod
    def interpolate(self, other: "Pattern", t: float) -> "Pattern":
        """Interpolate between this pattern and another pattern

        Args:
            other: Another Pattern object to interpolate with
            t: Interpolation factor (0 <= t <= 1), where 0 returns self and 1 returns other

        Returns:
            Interpolated Pattern object. For same-class patterns, values are smoothly
            interpolated. For different-class patterns, returns step interpolation
            (self if t < 0.5, else other).
        """
        pass
