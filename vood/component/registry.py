"""
Renderer registry for automatic state→renderer mapping.

This module provides a registry system that associates state classes with
their renderer classes via a decorator placed on the *state class*.

Usage:
    In renderer file:
        class CircleRenderer(Renderer):
            ...

    In state file:
        @renderer(CircleRenderer)
        class CircleState(VertexState):
            ...

    Subclasses can override manually if desired:
        class FancyCircleState(CircleState):
            def get_renderer_class(self):
                return FancyCircleRenderer
"""

from typing import Dict, Type, Optional, Any

# Maps state classes → renderer classes
_renderer_registry: Dict[Type, Type] = {}

# Singleton cache for stateless renderer instances
_renderer_cache: Dict[Type, Any] = {}


def renderer(renderer_class):
    """
    Decorator used ON A STATE CLASS to assign its renderer.

    Args:
        renderer_class: Either a renderer class or a callable that returns one (for lazy loading)

    Example:
        @renderer(CircleRenderer)
        class CircleState(VertexState):
            ...

        Or with lazy loading (to avoid circular imports):
        @renderer(lambda: CircleRenderer)
        class CircleState(VertexState):
            ...
    """
    def decorator(state_class: Type):
        # Prevent accidentally assigning multiple renderers to one state
        if state_class in _renderer_registry:
            # For error message, try to get name without importing
            prev_renderer = _renderer_registry[state_class]
            raise RuntimeError(
                f"State '{state_class.__name__}' is already registered with a renderer. "
                f"Cannot register multiple renderers for the same state."
            )

        # Store the original (possibly callable) renderer_class
        # Do NOT resolve it here - that would trigger imports during decoration
        _renderer_registry[state_class] = renderer_class
        return state_class

    return decorator


def get_renderer_class_for_state(state: Any) -> Optional[Type]:
    """
    Resolve the renderer class for the given state instance.
    State subclasses may override `get_renderer_class()` manually.

    Returns:
        Renderer class or None
    """
    cls = state.__class__

    # Manual override takes precedence
    if hasattr(state, "get_renderer_class"):
        custom = state.get_renderer_class()
        if custom is not None:
            return custom

    renderer_class_or_callable = _renderer_registry.get(cls)

    # If it's a callable (lazy loader), resolve it now and cache
    if callable(renderer_class_or_callable) and not isinstance(renderer_class_or_callable, type):
        renderer_class = renderer_class_or_callable()
        # Cache the resolved class for next time
        _renderer_registry[cls] = renderer_class
        return renderer_class

    return renderer_class_or_callable


def get_renderer_instance_for_state(state: Any) -> Any:
    """
    Retrieve the cached renderer instance for a state.
    Instantiates and caches the renderer automatically.
    """
    renderer_class = get_renderer_class_for_state(state)
    if renderer_class is None:
        raise RuntimeError(
            f"No renderer registered for state type: {state.__class__.__name__}. "
            f"Add @renderer(RendererClass) decorator to the state class definition."
        )

    # Cache renderer instances by their class
    if renderer_class not in _renderer_cache:
        _renderer_cache[renderer_class] = renderer_class()

    return _renderer_cache[renderer_class]


def is_renderer_registered_for_state(state_class: Type) -> bool:
    """Check whether a state class has a renderer registered."""
    return state_class in _renderer_registry


def get_all_registered_state_renderer_pairs():
    """Return list of (state_class, renderer_class) tuples."""
    return list(_renderer_registry.items())


def clear_renderer_cache():
    """Clear all cached renderer instances (useful for testing)."""
    _renderer_cache.clear()