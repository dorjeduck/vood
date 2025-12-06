"""Color matrix filter"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import drawsvg as dw

from .base import Filter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vood.core.color import Color


@dataclass(frozen=True)
class ColorMatrixFilter(Filter):
    """Color matrix filter for color transformations

    Args:
        matrix: 5x4 matrix for color transformation (20 values)
                Format: [r_r, r_g, r_b, r_a, r_offset,
                         g_r, g_g, g_b, g_a, g_offset,
                         b_r, b_g, b_b, b_a, b_offset,
                         a_r, a_g, a_b, a_a, a_offset]

    Example:
        >>> # Grayscale filter
        >>> grayscale = ColorMatrixFilter(matrix=[
        ...     0.33, 0.33, 0.33, 0, 0,
        ...     0.33, 0.33, 0.33, 0, 0,
        ...     0.33, 0.33, 0.33, 0, 0,
        ...     0,    0,    0,    1, 0
        ... ])
    """

    matrix: tuple[float, ...] = (
        1, 0, 0, 0, 0,
        0, 1, 0, 0, 0,
        0, 0, 1, 0, 0,
        0, 0, 0, 1, 0
    )

    def __post_init__(self):
        if len(self.matrix) != 20:
            raise ValueError(f"matrix must have exactly 20 values, got {len(self.matrix)}")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        # Format matrix as space-separated string
        matrix_str = " ".join(str(v) for v in self.matrix)
        return dw.FilterItem('feColorMatrix', type='matrix', values=matrix_str, in_='SourceGraphic')

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two ColorMatrixFilter instances"""
        if not isinstance(other, ColorMatrixFilter):
            return self if t < 0.5 else other

        # Interpolate each matrix value
        interpolated_matrix = tuple(
            self.matrix[i] + (other.matrix[i] - self.matrix[i]) * t
            for i in range(20)
        )

        return ColorMatrixFilter(matrix=interpolated_matrix)

    @classmethod
    def grayscale(cls, amount: float = 1.0) -> "ColorMatrixFilter":
        """Create a grayscale filter

        Args:
            amount: Grayscale amount (0 = no effect, 1 = full grayscale)
        """
        # Lerp between identity matrix and grayscale matrix
        identity = (1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0)
        gray = (0.33, 0.33, 0.33, 0, 0, 0.33, 0.33, 0.33, 0, 0, 0.33, 0.33, 0.33, 0, 0, 0, 0, 0, 1, 0)

        matrix = tuple(identity[i] + (gray[i] - identity[i]) * amount for i in range(20))
        return cls(matrix=matrix)

    @classmethod
    def sepia(cls, amount: float = 1.0) -> "ColorMatrixFilter":
        """Create a sepia filter

        Args:
            amount: Sepia amount (0 = no effect, 1 = full sepia)
        """
        identity = (1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0)
        sepia = (0.393, 0.769, 0.189, 0, 0, 0.349, 0.686, 0.168, 0, 0, 0.272, 0.534, 0.131, 0, 0, 0, 0, 0, 1, 0)

        matrix = tuple(identity[i] + (sepia[i] - identity[i]) * amount for i in range(20))
        return cls(matrix=matrix)


