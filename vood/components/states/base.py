from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, Field

from vood.transitions import easing


@dataclass
class State(ABC):
    """Abstract base class for all state classes

    Contains common visual properties that all renderers can use.
    Subclasses add renderer-specific properties.
    """

    x: float = 0
    y: float = 0
    scale: float = 1.0
    opacity: float = 1.0
    rotation: float = 0

    DEFAULT_EASING = {
        "x": easing.in_out,
        "y": easing.in_out,
        "scale": easing.in_out,
        "opacity": easing.linear,
        "rotation": easing.in_out,
    }

    # can be overridden by subclasses to add further angle fields
    # used in interpolation (shortest angle distance)

    def is_angle(self, field: Field):
        return field.name == "rotation"
