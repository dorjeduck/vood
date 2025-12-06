"""Visual effects for SVG components

This module provides visual effects that can be applied to components:
- Gradients: Linear and radial color gradients
- Patterns: Repeating texture patterns
- Filters: SVG filter effects (blur, shadow, morphology, etc.)
"""

from .gradient import Gradient, LinearGradient, RadialGradient, GradientStop
from .pattern import (
    Pattern,
    CustomPattern,
    DotsPattern,
    StripesPattern,
    GridPattern,
    CheckerboardPattern,
)
from .filter import (
    Filter,
    GaussianBlurFilter,
    DropShadowFilter,
    ColorMatrixFilter,
    CompositeFilter,
    OffsetFilter,
    MorphologyFilter,
    FloodFilter,
    BlendFilter,
    CompositeFilterPrimitive,
    TurbulenceFilter,
    DisplacementMapFilter,
    ConvolveMatrixFilter,
    TileFilter,
    ImageFilter,
    MergeNodeFilter,
)

__all__ = [
    # Gradients
    "Gradient",
    "LinearGradient",
    "RadialGradient",
    "GradientStop",
    # Patterns
    "Pattern",
    "CustomPattern",
    "DotsPattern",
    "StripesPattern",
    "GridPattern",
    "CheckerboardPattern",
    # Filters
    "Filter",
    "GaussianBlurFilter",
    "DropShadowFilter",
    "ColorMatrixFilter",
    "CompositeFilter",
    "OffsetFilter",
    "MorphologyFilter",
    "FloodFilter",
    "BlendFilter",
    "CompositeFilterPrimitive",
    "TurbulenceFilter",
    "DisplacementMapFilter",
    "ConvolveMatrixFilter",
    "TileFilter",
    "ImageFilter",
    "MergeNodeFilter",
]
