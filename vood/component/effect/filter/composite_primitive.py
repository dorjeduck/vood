"""Composite filter primitive"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import drawsvg as dw

from .base import Filter


class CompositeOperator(str, Enum):
    """Composite operators for CompositeFilterPrimitive"""
    OVER = 'over'
    IN = 'in'
    OUT = 'out'
    ATOP = 'atop'
    XOR = 'xor'
    LIGHTER = 'lighter'
    ARITHMETIC = 'arithmetic'


@dataclass(frozen=True)
class CompositeFilterPrimitive(Filter):
    """Composite filter - combines two inputs using Porter-Duff operations

    Args:
        operator: Composite operator ('over', 'in', 'out', 'atop', 'xor', 'lighter', 'arithmetic')
        in_: First input source
        in2: Second input source
        k1, k2, k3, k4: Arithmetic coefficients (only for operator='arithmetic')
                        result = k1*in*in2 + k2*in + k3*in2 + k4

    Example:
        >>> # Porter-Duff composite
        >>> comp = CompositeFilterPrimitive(operator='in', in_='SourceGraphic', in2='mask')
        >>> # Arithmetic composite
        >>> arith = CompositeFilterPrimitive(operator='arithmetic', k1=0, k2=1, k3=1, k4=0)
    """

    operator: str = 'over'
    in_: str = 'SourceGraphic'
    in2: str = 'SourceAlpha'
    k1: float = 0.0
    k2: float = 0.0
    k3: float = 0.0
    k4: float = 0.0

    def __post_init__(self):
        valid_operators = {op.value for op in CompositeOperator}
        if self.operator not in valid_operators:
            raise ValueError(f"operator must be one of {valid_operators}, got {self.operator}")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        kwargs = {
            'operator': self.operator,
            'in_': self.in_,
            'in2': self.in2
        }

        if self.operator == 'arithmetic':
            kwargs.update({
                'k1': self.k1,
                'k2': self.k2,
                'k3': self.k3,
                'k4': self.k4
            })

        return dw.FilterItem('feComposite', **kwargs)

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two CompositeFilterPrimitive instances"""
        if not isinstance(other, CompositeFilterPrimitive):
            return self if t < 0.5 else other

        operator = self.operator if t < 0.5 else other.operator
        in_ = self.in_ if t < 0.5 else other.in_
        in2 = self.in2 if t < 0.5 else other.in2

        # Interpolate k values for arithmetic mode
        k1 = self.k1 + (other.k1 - self.k1) * t
        k2 = self.k2 + (other.k2 - self.k2) * t
        k3 = self.k3 + (other.k3 - self.k3) * t
        k4 = self.k4 + (other.k4 - self.k4) * t

        return CompositeFilterPrimitive(
            operator=operator, in_=in_, in2=in2,
            k1=k1, k2=k2, k3=k3, k4=k4
        )


