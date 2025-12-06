"""Tile filter"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Filter


@dataclass(frozen=True)
class TileFilter(Filter):
    """Tile filter - repeats the input graphic as tiles

    Args:
        in_: Input source to tile

    Example:
        >>> tile = TileFilter(in_='SourceGraphic')
    """

    in_: str = 'SourceGraphic'

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        return dw.FilterItem('feTile', in_=self.in_)

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two TileFilter instances"""
        if not isinstance(other, TileFilter):
            return self if t < 0.5 else other

        in_ = self.in_ if t < 0.5 else other.in_
        return TileFilter(in_=in_)


