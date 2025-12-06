"""Radial gradient implementation"""

from __future__ import annotations
from dataclasses import dataclass

import drawsvg as dw

from .base import Gradient
from .gradient_stop import GradientStop


@dataclass(frozen=True)
class RadialGradient(Gradient):
    """Radial gradient from center point outward

    Args:
        cx, cy: Center point coordinates
        r: Radius of gradient
        stops: Tuple of GradientStop defining color transitions
    """

    cx: float
    cy: float
    r: float
    stops: tuple[GradientStop, ...]

    def __post_init__(self):
        if len(self.stops) < 2:
            raise ValueError(
                f"Gradient must have at least 2 stops, got {len(self.stops)}"
            )
        if self.r <= 0:
            raise ValueError(f"radius must be > 0, got {self.r}")

    def to_drawsvg(self) -> dw.RadialGradient:
        """Convert to drawsvg RadialGradient"""
        grad = dw.RadialGradient(self.cx, self.cy, self.r)
        for stop in self.stops:
            grad.add_stop(stop.offset, stop.color.to_hex(), stop.opacity)
        return grad

    def interpolate(self, other: Gradient, t: float) -> Gradient:
        """Interpolate between two RadialGradient instances"""
        if not isinstance(other, RadialGradient) or len(self.stops) != len(other.stops):
            # Step interpolation for different gradient types or mismatched stop counts
            return self if t < 0.5 else other

        # Interpolate position and radius values
        cx = self.cx + (other.cx - self.cx) * t
        cy = self.cy + (other.cy - self.cy) * t
        r = self.r + (other.r - self.r) * t

        # Interpolate stops
        interpolated_stops = []
        for s1, s2 in zip(self.stops, other.stops):
            offset = s1.offset + (s2.offset - s1.offset) * t
            color = s1.color.interpolate(s2.color, t)
            opacity = s1.opacity + (s2.opacity - s1.opacity) * t
            interpolated_stops.append(GradientStop(offset, color, opacity))

        return RadialGradient(cx, cy, r, tuple(interpolated_stops))
