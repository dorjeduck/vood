"""Abstract base class for renderers with multiple path variants"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from vood.component.state.base_color import ColorState

from .base import State
from vood.component.registry import renderer
from vood.component.renderer.path_variants import PathVariantsRenderer
from vood.transition import easing
from vood.core.color import Color


@renderer(PathVariantsRenderer)
@dataclass(frozen=True)
class PathVariantsState(ColorState):
    """Base state class for multi-path renderers"""

    size: float = 50
    case_sensitive: bool = False

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "size": easing.in_out,
    }

    def __post_init__(self):
        super().__post_init__()
        self._none_color("fill_color")
        self._none_color("stroke_color")
