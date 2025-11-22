from __future__ import annotations
from dataclasses import dataclass
from typing import Union, List, Optional
from .text import TextState

from vood.transition import easing


@dataclass(frozen=True)
class CircleTextState(TextState):
    """State class for text elements"""

    radius: float = 100  # Radius of the circle path
    rotation: float = 0
    angles: Optional[List[float]] = None

    text: Union[str, List[str]]
    text_facing_inward: bool = True
    font_family: str = "Arial"
    text_align: str = "middle"
    font_weight: str = "normal"
    text_anchor: str = "middle"
    dominant_baseline: str = "central"

    # Default easing functions for each property
    DEFAULT_EASING = {
        **TextState.DEFAULT_EASING,
        "radius": easing.in_out,
        "rotation": easing.in_out,
        "angles": easing.linear,
        "text": easing.step,
        "text_facing_inward": easing.step,
        "font_family": easing.step,
        "text_align": easing.step,
        "font_weight": easing.step,
        "text_anchor": easing.step,
        "dominant_baseline": easing.step,
    }

