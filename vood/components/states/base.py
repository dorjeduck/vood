from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, fields, Field
from typing import get_origin, get_args, Union, Any

from vood.transitions import easing
from vood.core import Color


@dataclass(frozen=True)
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

    def _none_color(self, field_name: str):
        color = getattr(self, field_name)
        if color is None:
            self._set_field(field_name, Color.NONE)

    def _normalize_color_field(self, field_name: str) -> None:
        """Normalize and set a color field in frozen dataclass

        Args:
            field_name: Name of the field to set

        """
        color = getattr(self, field_name)
        if color is None:
            normalized = Color.NONE
        elif isinstance(color, Color):
            normalized = color
        else:
            normalized = Color(color)

        object.__setattr__(self, field_name, normalized)

    def _set_field(self, name: str, value: Any) -> None:
        """Helper to set fields in frozen dataclass during __post_init__"""
        object.__setattr__(self, name, value)
