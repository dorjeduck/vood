"""Gradient effects for SVG fills and strokes"""

from .base import Gradient
from .gradient_stop import GradientStop
from .linear import LinearGradient
from .radial import RadialGradient

__all__ = [
    "Gradient",
    "GradientStop",
    "LinearGradient",
    "RadialGradient",
]
