"""Blend filter"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import drawsvg as dw

from .base import Filter


class BlendMode(str, Enum):
    """Blend modes for BlendFilter"""
    NORMAL = 'normal'
    MULTIPLY = 'multiply'
    SCREEN = 'screen'
    OVERLAY = 'overlay'
    DARKEN = 'darken'
    LIGHTEN = 'lighten'
    COLOR_DODGE = 'color-dodge'
    COLOR_BURN = 'color-burn'
    HARD_LIGHT = 'hard-light'
    SOFT_LIGHT = 'soft-light'
    DIFFERENCE = 'difference'
    EXCLUSION = 'exclusion'
    HUE = 'hue'
    SATURATION = 'saturation'
    COLOR = 'color'
    LUMINOSITY = 'luminosity'


@dataclass(frozen=True)
class BlendFilter(Filter):
    """Blend filter - blends two input graphics

    Args:
        mode: Blend mode ('normal', 'multiply', 'screen', 'darken', 'lighten', etc.)
        in_: First input source
        in2: Second input source

    Example:
        >>> blend = BlendFilter(mode='multiply', in_='SourceGraphic', in2='BackgroundImage')
    """

    mode: str = 'normal'
    in_: str = 'SourceGraphic'
    in2: str = 'BackgroundImage'

    def __post_init__(self):
        valid_modes = {mode.value for mode in BlendMode}
        if self.mode not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}, got {self.mode}")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        return dw.FilterItem(
            'feBlend',
            mode=self.mode,
            in_=self.in_,
            in2=self.in2
        )

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two BlendFilter instances"""
        if not isinstance(other, BlendFilter):
            return self if t < 0.5 else other

        # Step interpolation for mode and inputs
        mode = self.mode if t < 0.5 else other.mode
        in_ = self.in_ if t < 0.5 else other.in_
        in2 = self.in2 if t < 0.5 else other.in2

        return BlendFilter(mode=mode, in_=in_, in2=in2)


