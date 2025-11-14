# ============================================================================
# vood/animations/compound/__init__.py
# ============================================================================
"""
Compound Animations
===================

Multi-element animation patterns that return multiple keystate lists.

These functions generate coordinated keystates for multiple elements that
animate simultaneously. Each function returns a tuple of keystate lists,
one for each element involved in the transition.

All functions return: Tuple[List[Tuple[float, State]], List[Tuple[float, State]]]

Available animations:
- crossfade: Two elements fade simultaneously (one out, one in)
- slide_replace: Two elements slide past each other
- scale_swap: Two elements scale in opposite directions
- rotate_flip: Two elements create flip effect
- bounce_replace: Two elements bounce in sequence
"""

from .crossfade import crossfade
from .slide_replace import slide_replace, SlideDirection
from .scale_swap import scale_swap
from .rotate_flip import rotate_flip
from .bounce_replace import bounce_replace

__all__ = [
    "crossfade",
    "slide_replace",
    "SlideDirection",
    "scale_swap",
    "rotate_flip",
    "bounce_replace",
]
