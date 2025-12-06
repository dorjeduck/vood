"""Turbulence filter"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import drawsvg as dw

from .base import Filter


class TurbulenceType(str, Enum):
    """Turbulence types for TurbulenceFilter"""
    FRACTAL_NOISE = 'fractalNoise'
    TURBULENCE = 'turbulence'


class StitchTiles(str, Enum):
    """Stitch tile modes for TurbulenceFilter"""
    STITCH = 'stitch'
    NO_STITCH = 'noStitch'


@dataclass(frozen=True)
class TurbulenceFilter(Filter):
    """Turbulence filter - generates Perlin noise

    Args:
        type_: 'fractalNoise' or 'turbulence'
        base_frequency: Base frequency (can be single value or tuple for x,y)
        num_octaves: Number of octaves for noise function
        seed: Random seed for reproducible noise
        stitch_tiles: Whether to stitch tiles ('stitch' or 'noStitch')

    Example:
        >>> # Turbulence noise
        >>> turb = TurbulenceFilter(type_='turbulence', base_frequency=0.05, num_octaves=3)
        >>> # Fractal noise with different x,y frequencies
        >>> fractal = TurbulenceFilter(type_='fractalNoise', base_frequency=(0.01, 0.05))
    """

    type_: str = 'turbulence'
    base_frequency: float | tuple[float, float] = 0.05
    num_octaves: int = 1
    seed: int = 0
    stitch_tiles: str = 'noStitch'

    def __post_init__(self):
        valid_types = {t.value for t in TurbulenceType}
        if self.type_ not in valid_types:
            raise ValueError(f"type_ must be one of {valid_types}, got {self.type_}")
        if self.num_octaves < 1:
            raise ValueError(f"num_octaves must be >= 1, got {self.num_octaves}")
        valid_stitch = {s.value for s in StitchTiles}
        if self.stitch_tiles not in valid_stitch:
            raise ValueError(f"stitch_tiles must be one of {valid_stitch}, got {self.stitch_tiles}")

    def to_drawsvg(self) -> dw.FilterItem:
        """Convert to drawsvg FilterItem object"""
        if isinstance(self.base_frequency, tuple):
            freq_str = f"{self.base_frequency[0]} {self.base_frequency[1]}"
        else:
            freq_str = str(self.base_frequency)

        return dw.FilterItem(
            'feTurbulence',
            type=self.type_,
            baseFrequency=freq_str,
            numOctaves=self.num_octaves,
            seed=self.seed,
            stitchTiles=self.stitch_tiles
        )

    def interpolate(self, other: Filter, t: float):
        """Interpolate between two TurbulenceFilter instances"""
        if not isinstance(other, TurbulenceFilter):
            return self if t < 0.5 else other

        type_ = self.type_ if t < 0.5 else other.type_
        stitch_tiles = self.stitch_tiles if t < 0.5 else other.stitch_tiles

        # Interpolate num_octaves (round to nearest int)
        num_octaves = round(self.num_octaves + (other.num_octaves - self.num_octaves) * t)
        seed = round(self.seed + (other.seed - self.seed) * t)

        # Interpolate base_frequency
        if isinstance(self.base_frequency, tuple) and isinstance(other.base_frequency, tuple):
            base_frequency = (
                self.base_frequency[0] + (other.base_frequency[0] - self.base_frequency[0]) * t,
                self.base_frequency[1] + (other.base_frequency[1] - self.base_frequency[1]) * t
            )
        elif isinstance(self.base_frequency, tuple):
            base_frequency = self.base_frequency if t < 0.5 else other.base_frequency
        elif isinstance(other.base_frequency, tuple):
            base_frequency = self.base_frequency if t < 0.5 else other.base_frequency
        else:
            base_frequency = self.base_frequency + (other.base_frequency - self.base_frequency) * t

        return TurbulenceFilter(
            type_=type_,
            base_frequency=base_frequency,
            num_octaves=num_octaves,
            seed=seed,
            stitch_tiles=stitch_tiles
        )


