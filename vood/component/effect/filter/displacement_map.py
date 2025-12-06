"""Displacement map filter"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import drawsvg as dw

from .base import Filter


class ColorChannel(str, Enum):
    """Color channels for DisplacementMapFilter"""
    R = 'R'
    G = 'G'
    B = 'B'
    A = 'A'


@dataclass(frozen=True)
class DisplacementMapFilter(Filter):
    """Displacement map filter - distorts using another graphic

    Uses pixel values from in2 to spatially displace in.

    Args:
        scale: Displacement scale factor
        x_channel_selector: Channel to use for x displacement ('R', 'G', 'B', 'A')
        y_channel_selector: Channel to use for y displacement ('R', 'G', 'B', 'A')
        in_: Input source to displace
        in2: Displacement map source

    Example:
        >>> disp = DisplacementMapFilter(scale=20, x_channel_selector='R', y_channel_selector='G')
    """

    scale: float = 0.0
    x_channel_selector: str = 'A'
    y_channel_selector: str = 'A'
    in_: str = 'SourceGraphic'
    in2: str = 'SourceAlpha'

    def __post_init__(self):
        valid_channels = {channel.value for channel in ColorChannel}
        if self.x_channel_selector not in valid_channels:
            raise ValueError(f"x_channel_selector must be one of {valid_channels}, got {self.x_channel_selector}")
        if self.y_channel_selector not in valid_channels:
            raise ValueError(f"y_channel_selector must be one of {valid_channels}, got {self.y_channel_selector}")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        return dw.FilterItem(
            'feDisplacementMap',
            scale=self.scale,
            xChannelSelector=self.x_channel_selector,
            yChannelSelector=self.y_channel_selector,
            in_=self.in_,
            in2=self.in2
        )

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two DisplacementMapFilter instances"""
        if not isinstance(other, DisplacementMapFilter):
            return self if t < 0.5 else other

        scale = self.scale + (other.scale - self.scale) * t
        x_channel_selector = self.x_channel_selector if t < 0.5 else other.x_channel_selector
        y_channel_selector = self.y_channel_selector if t < 0.5 else other.y_channel_selector
        in_ = self.in_ if t < 0.5 else other.in_
        in2 = self.in2 if t < 0.5 else other.in2

        return DisplacementMapFilter(
            scale=scale,
            x_channel_selector=x_channel_selector,
            y_channel_selector=y_channel_selector,
            in_=in_,
            in2=in2
        )


