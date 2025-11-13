# ============================================================================
# vood/animations/compound/crossfade.py
# ============================================================================
"""Crossfade between two elements with simultaneous fade"""

from typing import List, Tuple
from dataclasses import replace
from vood.component import State


def crossfade(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.3,
    extend_timeline: bool = False,
) -> Tuple[List[Tuple[float, State]], List[Tuple[float, State]]]:
    """Crossfade between two elements with simultaneous opacity transition

    First element fades out while second element fades in at the same time.
    Both elements are visible during the transition, creating a smooth blend.

    Args:
        state1: Starting state (will fade out)
        state2: Ending state (will fade in)
        at_time: Center point of the crossfade (0.0 to 1.0)
        duration: Duration of the crossfade overlap (0.0 to 1.0)
        extend_timeline: If True, adds keystates at 0.0 and 1.0 to cover full timeline

    Returns:
        Tuple of (element1_keyframes, element2_keyframes)

    Example:
        >>> from vood.animations.compound import crossfade
        >>> from vood import VElement, VElementGroup
        >>>
        >>> kf1, kf2 = crossfade(
        ...     TextState(text="Hello", x=100),
        ...     TextState(text="World", x=100),
        ...     at_time=0.5,
        ...     duration=0.4
        ... )
        >>>
        >>> elem1 = VElement(text_renderer, keystates=kf1)
        >>> elem2 = VElement(text_renderer, keystates=kf2)
        >>> group = VElementGroup(elements=[elem1, elem2])
    """
    half = duration / 2
    t_start = at_time - half
    t_end = at_time + half

    # Element 1: Fade from 1.0 to 0.0
    keyframes1 = [
        (t_start, replace(state1, opacity=1.0)),
        (t_end, replace(state1, opacity=0.0)),
    ]

    # Element 2: Fade from 0.0 to 1.0
    keyframes2 = [
        (t_start, replace(state2, opacity=0.0)),
        (t_end, replace(state2, opacity=1.0)),
    ]

    if extend_timeline:
        keyframes1 = [
            (0.0, replace(state1, opacity=1.0)),
            *keyframes1,
        ]
        keyframes2 = [
            *keyframes2,
            (1.0, replace(state2, opacity=1.0)),
        ]

    return keyframes1, keyframes2
