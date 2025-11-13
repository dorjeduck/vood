# ============================================================================
# vood/animations/atomic/hold.py
# ============================================================================
"""Hold and instant switch animation"""

from typing import List, Tuple
from vood.components import State


def step(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    extend_timeline: bool = False,
) -> List[Tuple[float, State]]:
    """Hold first state, then instantly switch to second state

    Creates a step transition with no interpolation between states.
    Useful for countdowns, step-by-step reveals, or any instant change.

    Args:
        state1: Starting state (will be held)
        state2: Ending state (appears instantly)
        at_time: Time when the switch occurs (0.0 to 1.0)
        extend_timeline: If True, adds keyframes at 0.0 and 1.0 to cover full timeline

    Returns:
        List of keyframes for single element

    Example:
        >>> # Element only exists at transition point
        >>> from vood.magic.animations.atomic import hold
        >>>
        >>> keyframes = hold(
        ...     TextState(text="Before"),
        ...     TextState(text="After"),
        ...     at_time=0.5
        ... )
        >>> element = VElement(renderer, keyframes=keyframes)
        >>> # Element appears at 0.5, switches instantly

        >>> # Countdown sequence
        >>> keyframes = [
        ...     (0.0, TextState(text="3")),
        ...     *hold(TextState(text="3"), TextState(text="2"), at_time=0.33),
        ...     *hold(TextState(text="2"), TextState(text="1"), at_time=0.66),
        ...     (1.0, TextState(text="1")),
        ... ]
    """
    keyframes = [
        (at_time, state1),
        (at_time, state2),  # Duplicate time = instant switch
    ]

    if extend_timeline:
        keyframes = [
            (0.0, state1),
            *keyframes,
            (1.0, state2),
        ]

    return keyframes
