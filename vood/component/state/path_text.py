# ============================================================================
# vood/components/path_text.py
# ============================================================================
"""PathText component - Text that follows any SVG path with morphing support"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union, List, Optional

from .text import TextState
from vood.path import SVGPath
from vood.transition import easing


@dataclass(frozen=True)
class PathTextState(TextState):
    """State class for text elements following an SVG path

    Supports text morphing by animating the path property.
    """

    data: Union[str, SVGPath] = "M 0,0 L 10,10 L 0,20 Z"  # Default straight line path
    offset: float = 0.5  # Position along path (0.0 to 1.0)
    offsets: Optional[List[float]] = None  # For multiple texts

    text: Union[str, List[str]] = "Text"

    # Path rendering options
    flip_text: bool = False  # Flip text upside down (for bottom of curves)

    # Default easing functions for each property
    DEFAULT_EASING = {
        **TextState.DEFAULT_EASING,
        "path": easing.in_out,  # SVGPath will morph smoothly!
        "offset": easing.in_out,
        "offsets": easing.linear,
        "flip_text": easing.step,
    }

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.data, str):
            self.data = SVGPath.from_string(self.data)

    @staticmethod
    def get_renderer_class():
        from ..renderer.path_text import PathTextRenderer

        return PathTextRenderer
