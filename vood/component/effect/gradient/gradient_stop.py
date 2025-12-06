"""Gradient stop for color transitions in gradients"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vood.core.color import Color


@dataclass(frozen=True)
class GradientStop:
    """A color stop in a gradient

    Args:
        offset: Position along gradient (0.0 to 1.0)
        color: Color at this stop
        opacity: Opacity at this stop (0.0 to 1.0)
    """

    offset: float
    color: Color
    opacity: float = 1.0

    def __post_init__(self):
        if not 0 <= self.offset <= 1:
            raise ValueError(f"offset must be 0-1, got {self.offset}")
        if not 0 <= self.opacity <= 1:
            raise ValueError(f"opacity must be 0-1, got {self.opacity}")
