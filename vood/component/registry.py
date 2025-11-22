"""Renderer registry for automatic state-renderer mapping.

This module provides a registry system that automatically maps state classes
to their corresponding renderer classes using decorators, reducing boilerplate
in state class definitions.

Usage:
    In renderer file:
        @register_renderer(CircleState)
        class CircleRenderer(Renderer):
            ...

    In state file:
        # No need to define get_renderer_class() anymore
        class CircleState(VertexState):
            ...

    Users can still override:
        class MyCustomState(CircleState):
            def get_renderer_class(self):
                return MyCustomRenderer
"""

from typing import Dict, Type, Optional

# Global registry mapping state classes to renderer classes
_renderer_registry: Dict[Type, Type] = {}


def register_renderer(state_class: Type):
    """Decorator to register a renderer for a state class.

    Args:
        state_class: The state class this renderer handles

    Returns:
        Decorator function that registers the renderer

    Example:
        @register_renderer(CircleState)
        class CircleRenderer(Renderer):
            ...
    """
    def decorator(renderer_class: Type):
        _renderer_registry[state_class] = renderer_class
        return renderer_class
    return decorator


def get_renderer_for_state(state_class: Type) -> Optional[Type]:
    """Get the registered renderer for a state class.

    Args:
        state_class: The state class to look up

    Returns:
        The renderer class, or None if not registered
    """
    return _renderer_registry.get(state_class)


def is_renderer_registered(state_class: Type) -> bool:
    """Check if a renderer is registered for a state class.

    Args:
        state_class: The state class to check

    Returns:
        True if a renderer is registered, False otherwise
    """
    return state_class in _renderer_registry


def get_all_registered_states():
    """Get all state classes that have registered renderers.

    Returns:
        List of state classes
    """
    return list(_renderer_registry.keys())
