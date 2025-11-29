# ============================================================================
# vood/animations/compound/scale_swap.py
# ============================================================================
"""Scale swap with two elements scaling in opposite directions"""

from typing import Tuple
from dataclasses import replace
from vood.component import State
from vood.velement.keystate import KeyState, KeyStates

def scale_swap(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.3,
    min_scale: float = 0.0,
    extend_timeline: bool = False,
) -> Tuple[KeyStates, KeyStates]:
    """Scale down first element while scaling up second element

    First element scales down to minimum while second element scales up
    from minimum. Both elements are visible during the transition, creating
    a smooth "swap" effect. Works great with elastic or bounce easing.

    Args:
        state1: Starting state (will scale down)
        state2: Ending state (will scale up)
        at_time: Center point of the transition (0.0 to 1.0)
        duration: Duration of the scale transition (0.0 to 1.0)
        min_scale: Minimum scale value (0.0 = invisible)
        extend_timeline: If True, adds keystates at 0.0 and 1.0 to cover full timeline

    Returns:
        Tuple of (element1_keyframes, element2_keyframes)

    Example:
        >>> from vood.animations.compound import scale_swap
        >>> from vood.transitions import easing
        >>> from vood import VElement, VElementGroup
        >>>
        >>> kf1, kf2 = scale_swap(
        ...     CircleState(radius=50),
        ...     CircleState(radius=50, fill=(255, 0, 0)),
        ...     at_time=0.5
        ... )
        >>>
        >>> elem1 = VElement(circle_renderer, keystates=kf1)
        >>> elem2 = VElement(circle_renderer, keystates=kf2,
        ...                  property_easing={"scale": easing.elastic})
        >>> group = VElementGroup(elements=[elem1, elem2])
    """
    half = duration / 2
    t_start = at_time - half
    t_end = at_time + half

    # Element 1: Scale from 1.0 to min_scale
    keyframes1 = [
        KeyState(time=t_start, state=replace(state1, scale=1.0, opacity=1.0)),
        KeyState(time=t_end, state=replace(state1, scale=min_scale, opacity=0.0)),
    ]

    # Element 2: Scale from min_scale to 1.0
    keyframes2 = [
        KeyState(time=t_start, state=replace(state2, scale=min_scale, opacity=0.0)),
        KeyState(time=t_end, state=replace(state2, scale=1.0, opacity=1.0)),
    ]

    if extend_timeline:
        keyframes1 = [
            KeyState(time=0.0, state=replace(state1, scale=1.0, opacity=1.0)),
            *keyframes1,
        ]
        keyframes2 = [
            *keyframes2,
            KeyState(time=1.0, state=replace(state2, scale=1.0, opacity=1.0)),
        ]

    return keyframes1, keyframes2
