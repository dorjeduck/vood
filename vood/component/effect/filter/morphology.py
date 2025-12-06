"""Morphology filter"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import drawsvg as dw

from .base import Filter


class MorphologyOperator(str, Enum):
    """Morphology operators for MorphologyFilter"""
    ERODE = 'erode'
    DILATE = 'dilate'


@dataclass(frozen=True)
class MorphologyFilter(Filter):
    """Morphology filter - erode or dilate effect

    Args:
        operator: 'erode' or 'dilate'
        radius: Morphology radius (can be single value or tuple for x,y)
        in_: Input source (default: 'SourceGraphic')

    Example:
        >>> erode = MorphologyFilter(operator='erode', radius=2)
        >>> dilate = MorphologyFilter(operator='dilate', radius=3)
    """

    operator: str = 'erode'
    radius: float | tuple[float, float] = 1.0
    in_: str = 'SourceGraphic'

    def __post_init__(self):
        valid_operators = {op.value for op in MorphologyOperator}
        if self.operator not in valid_operators:
            raise ValueError(f"operator must be one of {valid_operators}, got {self.operator}")
        if isinstance(self.radius, (int, float)) and self.radius < 0:
            raise ValueError(f"radius must be >= 0, got {self.radius}")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        if isinstance(self.radius, tuple):
            radius_str = f"{self.radius[0]} {self.radius[1]}"
        else:
            radius_str = str(self.radius)

        kwargs = {'operator': self.operator, 'radius': radius_str}
        if self.in_:
            kwargs['in_'] = self.in_
        return dw.FilterItem('feMorphology', **kwargs)

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two MorphologyFilter instances"""
        if not isinstance(other, MorphologyFilter):
            return self if t < 0.5 else other

        operator = self.operator if t < 0.5 else other.operator
        in_ = self.in_ if t < 0.5 else other.in_

        # Interpolate radius
        if isinstance(self.radius, tuple) and isinstance(other.radius, tuple):
            radius = (
                self.radius[0] + (other.radius[0] - self.radius[0]) * t,
                self.radius[1] + (other.radius[1] - self.radius[1]) * t
            )
        elif isinstance(self.radius, tuple):
            other_val = other.radius if isinstance(other.radius, (int, float)) else other.radius[0]
            if t < 0.5:
                radius = self.radius
            else:
                radius = other_val
        elif isinstance(other.radius, tuple):
            self_val = self.radius
            if t < 0.5:
                radius = self_val
            else:
                radius = other.radius
        else:
            radius = self.radius + (other.radius - self.radius) * t

        return MorphologyFilter(operator=operator, radius=radius, in_=in_)


