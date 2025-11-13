from dataclasses import dataclass
from typing import Optional, Union
from enum import StrEnum

from vood.path.svg_path import SVGPath
from vood.core.color import Color

from .base import State
from vood.transition import easing


class MorphMethod(StrEnum):
    """Path morphing method selection"""

    STROKE = "stroke"  # Native engine for open paths/strokes
    SHAPE = "shape"  # Flubber for closed shapes/fills
    AUTO = "auto"  # Auto-detect based on path structure


class StrokeLinecap(StrEnum):
    """SVG stroke-linecap values"""

    BUTT = "butt"
    ROUND = "round"
    SQUARE = "square"


class StrokeLinejoin(StrEnum):
    """SVG stroke-linejoin values"""

    MITER = "miter"
    ROUND = "round"
    BEVEL = "bevel"


class FillRule(StrEnum):
    """SVG fill-rule values"""

    NONZERO = "nonzero"
    EVENODD = "evenodd"


@dataclass(frozen=True)
class PathState(State):
    """State for SVG path rendering and morphing"""

    data: Union[str, SVGPath] = "M 0,0 L 10,10 L 0,20 Z"  # Default path data

    # Stroke properties
    stroke_color: Optional[Color] = None
    stroke_width: float = 1.0
    stroke_opacity: float = 1.0
    stroke_linecap: Union[StrokeLinecap, str] = StrokeLinecap.BUTT
    stroke_linejoin: Union[StrokeLinejoin, str] = StrokeLinejoin.MITER
    stroke_dasharray: Optional[str] = None

    # Fill properties
    fill_color: Optional[Color] = None
    fill_opacity: float = 1.0
    fill_rule: Union[str, FillRule] = FillRule.EVENODD  # nonzero, evenodd

    # General properties
    opacity: float = 1.0

    # Morphing method
    morph_method: Optional[Union[MorphMethod, str]] = None

    # Default easing for PathState
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "data": easing.linear,  # Linear interpolation for paths
        "stroke_color": easing.linear,
        "fill_color": easing.linear,
        "fill_opacity": easing.linear,
        "stroke_opacity": easing.linear,
        "stroke_width": easing.linear,
        "stroke_dasharray": easing.step,
        "stroke_linecap": easing.step,
        "stroke_linejoin": easing.step,
        "fill_rule": easing.step,
    }

    def __post_init__(self):
        super().__post_init__()

        if isinstance(self.data, str):
            self._set_field("data", SVGPath.from_string(self.data))

        self._none_color("fill_color")
        self._none_color("stroke_color")

    @staticmethod
    def get_renderer_class():
        from ..renderer.path import PathRenderer

        return PathRenderer
