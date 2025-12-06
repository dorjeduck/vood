"""Convolve matrix filter"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import drawsvg as dw

from .base import Filter


class EdgeMode(str, Enum):
    """Edge modes for ConvolveMatrixFilter"""
    DUPLICATE = 'duplicate'
    WRAP = 'wrap'
    NONE = 'none'


@dataclass(frozen=True)
class ConvolveMatrixFilter(Filter):
    """Convolve matrix filter - applies a convolution matrix

    Args:
        kernel_matrix: Convolution kernel (tuple of values)
        order: Matrix dimensions (single int for NxN or tuple for MxN)
        divisor: Divisor for the kernel (auto-calculated if None)
        bias: Bias to add to result
        target_x: X position of convolution target pixel
        target_y: Y position of convolution target pixel
        edge_mode: How to handle edges ('duplicate', 'wrap', 'none')
        preserve_alpha: Whether to preserve alpha channel

    Example:
        >>> # 3x3 sharpen kernel
        >>> sharpen = ConvolveMatrixFilter(
        ...     kernel_matrix=(0, -1, 0, -1, 5, -1, 0, -1, 0),
        ...     order=3
        ... )
    """

    kernel_matrix: tuple[float, ...]
    order: int | tuple[int, int] = 3
    divisor: Optional[float] = None
    bias: float = 0.0
    target_x: Optional[int] = None
    target_y: Optional[int] = None
    edge_mode: str = 'duplicate'
    preserve_alpha: bool = False
    in_: str = 'SourceGraphic'

    def __post_init__(self):
        valid_edge_modes = {mode.value for mode in EdgeMode}
        if self.edge_mode not in valid_edge_modes:
            raise ValueError(f"edge_mode must be one of {valid_edge_modes}, got {self.edge_mode}")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        if isinstance(self.order, tuple):
            order_str = f"{self.order[0]} {self.order[1]}"
        else:
            order_str = f"{self.order}"

        kernel_str = " ".join(str(v) for v in self.kernel_matrix)

        kwargs = {
            'order': order_str,
            'kernelMatrix': kernel_str,
            'bias': self.bias,
            'edgeMode': self.edge_mode,
            'preserveAlpha': 'true' if self.preserve_alpha else 'false'
        }

        if self.divisor is not None:
            kwargs['divisor'] = self.divisor
        if self.target_x is not None:
            kwargs['targetX'] = self.target_x
        if self.target_y is not None:
            kwargs['targetY'] = self.target_y
        if self.in_:
            kwargs['in_'] = self.in_

        return dw.FilterItem('feConvolveMatrix', **kwargs)

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two ConvolveMatrixFilter instances"""
        if not isinstance(other, ConvolveMatrixFilter):
            return self if t < 0.5 else other

        # Step interpolation for most properties
        return self if t < 0.5 else other


