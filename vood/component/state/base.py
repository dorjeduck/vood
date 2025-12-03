from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, Field
from typing import Any, Optional, List

from vood.transition import easing
from vood.core.color import Color
from vood.component.registry import get_renderer_class_for_state


@dataclass(frozen=True)
class State(ABC):
    """Abstract base class for all state classes

    Contains common visual properties that all renderers can use.
    Subclasses add renderer-specific properties.

    Default values for x, y, scale, opacity, and rotation are read from
    the configuration system if not explicitly provided.
    """

    x: Optional[float] = None
    y: Optional[float] = None
    scale: Optional[float] = None
    opacity: Optional[float] = None
    rotation: Optional[float] = None

    # Clipping and masking support
    clip_state: Optional[State] = None
    mask_state: Optional[State] = None
    clip_states: Optional[List[State]] = None
    mask_states: Optional[List[State]] = None

    # Fields that should not be interpolated (structural/configuration properties)
    NON_INTERPOLATABLE_FIELDS: frozenset[str] = frozenset(
        ["NON_INTERPOLATABLE_FIELDS", "DEFAULT_EASING"]
    )

    DEFAULT_EASING = {
        "x": easing.in_out,
        "y": easing.in_out,
        "scale": easing.in_out,
        "opacity": easing.linear,
        "rotation": easing.in_out,
        "clip_state": easing.linear,
        "mask_state": easing.linear,
        "clip_states": easing.linear,
        "mask_states": easing.linear,
    }

    # can be overridden by subclasses to add further angle fields
    # used in interpolation (shortest angle distance)

    def __post_init__(self):
        """Apply configuration defaults for common properties if not explicitly set"""
        from vood.config import get_config, ConfigKey

        config = get_config()

        # Apply config defaults for common properties if they are None
        if self.x is None:
            self._set_field("x", config.get(ConfigKey.STATE_X, 0.0))
        if self.y is None:
            self._set_field("y", config.get(ConfigKey.STATE_Y, 0.0))
        if self.scale is None:
            self._set_field("scale", config.get(ConfigKey.STATE_SCALE, 1.0))
        if self.opacity is None:
            self._set_field("opacity", config.get(ConfigKey.STATE_OPACITY, 1.0))
        if self.rotation is None:
            self._set_field("rotation", config.get(ConfigKey.STATE_ROTATION, 0.0))

    def get_renderer_class(self):
        """Get the renderer class for this state.

        Returns the renderer registered via the @renderer decorator.
        Subclasses can override this method to provide custom renderers.

        Returns:
            The renderer class for this state, or None if not registered

        Note:
            This method should return None to use the registry,
            or return a specific renderer class to override.
        """
        # Base implementation returns None to signal "use the registry"
        # Subclasses can override to return a specific renderer class
        return None

    def get_vertex_renderer_class(self):
        """Get the vertex renderer class for morphing transitions.

        By default, returns the same as get_renderer_class().
        VertexState subclass overrides this to return VertexRenderer.
        """
        return self.get_renderer_class()

    def need_morph(self, state):
        return type(state) is not type(self)

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


States = list[State]
