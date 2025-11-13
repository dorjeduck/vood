"""Interpolation functions for smooth transitions"""

from .lerp import lerp
from .color import color
from .angle import angle
from .step import step
from .morpher import FlubberMorpher, NativeMorpher
#from .morpher.svg_path import svg_path
#from .morpher.flubber_morpher import svg_shape, cleanup_shape_interpolator

__all__ = [
    "lerp",
    "color",
    "angle",
    "step",
    "FlubberMorpher",
    "NativeMorpher",
    "cleanup_shape_interpolator",
]
