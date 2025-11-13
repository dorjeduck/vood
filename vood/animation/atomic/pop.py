# ============================================================================
# vood/animations/atomic/pop.py
# ============================================================================
"""Pop animation - scale to zero and back with bounce"""

from typing import List, Tuple
from dataclasses import replace
from vood.component import State


def pop(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.2,
    extend_timeline: bool = False,
) -> List[Tuple[float, State]]:
    """Quick scale down to zero, switch, and scale back with overshoot

    Creates a "pop" effect by quickly scaling to zero and back.
    Good for playful, energetic transitions. Use with elastic or bounce
    easing for best effect.

    Args:
        state1: Starting state (will pop out)
        state2: Ending state (will pop in)
        at_time: Center point of the pop (0.0 to 1.0)
        duration: Total duration of the pop (0.0 to 1.0)
        extend_timeline: If True, adds keystates at 0.0 and 1.0 to cover full timeline

    Returns:
        List of keystates for single element

    Example:
        >>> from vood.animations.atomic import pop
        >>> from vood.transitions import easing
        >>>
        >>> # Element only exists during pop (partial timeline)
        >>> keystates = pop(
        ...     IconState(icon="heart", scale=1.0),
        ...     IconState(icon="star", scale=1.0),
        ...     at_time=0.5,
        ...     duration=0.3
        ... )
        >>> element = VElement(
        ...     renderer,
        ...     keystates=keystates,
        ...     property_easing={"scale": easing.elastic}  # Add bounce!
        ... )
    """
    half = duration / 2
    t_start = at_time - half
    t_end = at_time + half

    keystates = [
        (t_start, replace(state1, scale=1.0)),
        (at_time, replace(state1, scale=0.0)),  # Popped to zero
        (at_time, replace(state2, scale=0.0)),  # Switch (invisible)
        (t_end, replace(state2, scale=1.0)),  # Pop back
    ]

    if extend_timeline:
        keystates = [
            (0.0, replace(state1, scale=1.0)),
            *keystates,
            (1.0, replace(state2, scale=1.0)),
        ]

    return keystates
