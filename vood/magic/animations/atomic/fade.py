# ============================================================================
# vood/animations/atomic/fade.py
# ============================================================================
"""Fade out, switch, fade in animation"""

from typing import List, Tuple
from dataclasses import replace
from vood.components import State


def fade(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.2,
    extend_timeline: bool = False,
) -> List[Tuple[float, State]]:
    """Fade out first state, switch properties, fade in second state

    Creates a crossfade effect on a single element by fading to transparent,
    switching properties, then fading back to opaque.

    Args:
        state1: Starting state (will fade out)
        state2: Ending state (will fade in)
        at_time: Center point of the fade (0.0 to 1.0)
        duration: Total duration of fade out + fade in (0.0 to 1.0)
        extend_timeline: If True, adds keyframes at 0.0 and 1.0 to cover full timeline

    Returns:
        List of keyframes for single element

    Example:
        >>> from vood.magic.animations.atomic import fade
        >>>
        >>> # Element only exists during fade (partial timeline)
        >>> keyframes = fade(
        ...     TextState(text="Hello", x=100),
        ...     TextState(text="World", x=100),
        ...     at_time=0.5,
        ...     duration=0.3
        ... )
        >>> element = VElement(renderer, keyframes=keyframes)
        >>> # Element appears at ~0.35, fades through transition, disappears at ~0.65
    """
    half = duration / 2
    t_start = at_time - half
    t_end = at_time + half

    keyframes = [
        (t_start, replace(state1, opacity=1.0)),
        (at_time, replace(state1, opacity=0.0)),  # Faded out
        (at_time, replace(state2, opacity=0.0)),  # Switch (invisible)
        (t_end, replace(state2, opacity=1.0)),
    ]

    if extend_timeline:
        keyframes = [
            (0.0, replace(state1, opacity=1.0)),
            *keyframes,
            (1.0, replace(state2, opacity=1.0)),
        ]

    return keyframes
