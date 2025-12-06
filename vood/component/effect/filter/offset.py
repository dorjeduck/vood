"""Offset filter"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Filter


@dataclass(frozen=True)
class OffsetFilter(Filter):
    """Offset filter - shifts the graphic by dx, dy

    Often used to create drop shadows by offsetting before blurring.

    Args:
        dx: Horizontal offset
        dy: Vertical offset
        in_: Input source (default: 'SourceGraphic')

    Example:
        >>> offset = OffsetFilter(dx=10, dy=10)
    """

    dx: float = 0.0
    dy: float = 0.0
    in_: str = 'SourceGraphic'

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        kwargs = {'dx': self.dx, 'dy': self.dy}
        if self.in_:
            kwargs['in_'] = self.in_
        return dw.FilterItem('feOffset', **kwargs)

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two OffsetFilter instances"""
        if not isinstance(other, OffsetFilter):
            return self if t < 0.5 else other

        dx = self.dx + (other.dx - self.dx) * t
        dy = self.dy + (other.dy - self.dy) * t
        in_ = self.in_ if t < 0.5 else other.in_

        return OffsetFilter(dx=dx, dy=dy, in_=in_)


