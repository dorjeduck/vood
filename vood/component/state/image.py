"""Image renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
from enum import StrEnum


from .base import State
from vood.transition import easing
from vood.core.color import Color


class ImageFitMode(StrEnum):
    """Different modes for fitting images into the specified dimensions"""

    FIT = "fit"  # Scale to fit entirely within bounds
    FILL = "fill"  # Scale to fill bounds completely, cropping if needed
    CROP = "crop"  # Keep original size, crop to bounds
    STRETCH = "stretch"  # Stretch to exact dimensions (changes aspect ratio)
    ORIGINAL = "original"  # Keep original size, warn if doesn't fit
    RANDOM_CROP = (
        "random_crop"  # Randomly cut a section to fit bounds, randomly rotated/flipped
    )


@dataclass(frozen=True)
class ImageState(State):
    """State class for image elements"""

    href: str = ""  # Path or URL to the image file
    width: Optional[float] = None  # Image width (None = use original image width)
    height: Optional[float] = None  # Image height (None = use original image height)
    opacity: float = 1.0  # Image opacity (0.0 to 1.0)
    stroke_color: Optional[Color] = None  # Border color
    stroke_opacity: float = 1
    stroke_width: float = 0  # Border width
    fit_mode: ImageFitMode = ImageFitMode.FIT  # How to fit the image

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "width": easing.in_out,
        "height": easing.in_out,
        "stroke_color": easing.linear,
        "stroke_opacity": easing.linear,
        "stroke_width": easing.in_out,
    }

    def __post_init__(self):
        self._none_color("stroke_color")

    @staticmethod
    def get_renderer_class():
        from ..renderer.image import ImageRenderer

        return ImageRenderer
