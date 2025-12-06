"""Linear gradient implementation"""

from __future__ import annotations
from dataclasses import dataclass

import drawsvg as dw

from .base import Gradient
from .gradient_stop import GradientStop


@dataclass(frozen=True)
class LinearGradient(Gradient):
    """Linear gradient between two points

    Args:
        x1, y1: Start point coordinates
        x2, y2: End point coordinates
        stops: Tuple of GradientStop defining color transitions
    """

    x1: float
    y1: float
    x2: float
    y2: float
    stops: tuple[GradientStop, ...]

    def __post_init__(self):
        if len(self.stops) < 2:
            raise ValueError(
                f"Gradient must have at least 2 stops, got {len(self.stops)}"
            )

    def to_drawsvg(self) -> dw.LinearGradient:
        """Convert to drawsvg LinearGradient"""
        grad = dw.LinearGradient(self.x1, self.y1, self.x2, self.y2)
        for stop in self.stops:
            grad.add_stop(stop.offset, stop.color.to_hex(), stop.opacity)
        return grad

    def interpolate(self, other: Gradient, t: float) -> Gradient:
        """Interpolate between two LinearGradient instances"""
        if not isinstance(other, LinearGradient) or len(self.stops) != len(other.stops):
            # Step interpolation for different gradient types or mismatched stop counts
            return self if t < 0.5 else other

        # Interpolate position values
        x1 = self.x1 + (other.x1 - self.x1) * t
        y1 = self.y1 + (other.y1 - self.y1) * t
        x2 = self.x2 + (other.x2 - self.x2) * t
        y2 = self.y2 + (other.y2 - self.y2) * t

        # Interpolate stops
        interpolated_stops = []
        for s1, s2 in zip(self.stops, other.stops):
            offset = s1.offset + (s2.offset - s1.offset) * t
            color = s1.color.interpolate(s2.color, t)
            opacity = s1.opacity + (s2.opacity - s1.opacity) * t
            interpolated_stops.append(GradientStop(offset, color, opacity))

        return LinearGradient(x1, y1, x2, y2, tuple(interpolated_stops))
