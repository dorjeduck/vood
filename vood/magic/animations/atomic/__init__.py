# ============================================================================
# vood/animations/atomic/__init__.py
# ============================================================================
"""
Atomic Animations
=================

Single-element animation patterns that return one keystate list.

These functions generate keystates for animating a single element through
different states. The element changes its properties over time, with instant
switches or smooth transitions between values.

All functions return: List[Tuple[float, State]]

Available animations:
- hold: Hold state, then instantly switch
- fade: Fade out, switch, fade in
- slide: Slide out, switch, slide in
- scale: Scale down, switch, scale up
- rotate: Rotate out, switch, rotate in
- pop: Scale to zero, switch, scale from zero
"""

from .step import step
from .fade import fade
from .slide import slide
from .scale import scale
from .trim import trim
from .rotate import rotate
from .pop import pop
from .sequential_transition import sequential_transition

__all__ = [
    "step",
    "hold",
    "fade",
    "pop",
    "rotate",
    "slide",
    "scale",
    "trim",
    "sequential_transition",
]
