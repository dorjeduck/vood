# ============================================================================
# vood/animations/compound/slide_replace.py
# ============================================================================
"""Slide replace with two elements sliding past each other"""

from typing import Tuple, Union
from dataclasses import replace
from vood.component import State
from ..enums import SlideDirection
from vood.velement.keystate import KeyState, KeyStates


def slide_replace(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.3,
    direction: Union[SlideDirection, str] = SlideDirection.LEFT,
    distance: float = 100,
    extend_timeline: bool = False,
) -> Tuple[KeyStates, KeyStates]:
    """Slide two elements past each other simultaneously

    First element slides out in one direction while second element slides
    in from the opposite direction. Both elements are visible during the
    transition, creating a smooth sliding replacement.

    Args:
        state1: Starting state (will slide out)
        state2: Ending state (will slide in)
        at_time: Center point of the transition (0.0 to 1.0)
        duration: Duration of the slide (0.0 to 1.0)
        direction: Direction state1 slides out (SlideDirection enum or string)
        distance: Distance to slide in pixels
        extend_timeline: If True, adds keystates at 0.0 and 1.0 to cover full timeline

    Returns:
        Tuple of (element1_keyframes, element2_keyframes)

    Example:
        >>> from vood.animations.compound import slide_replace, SlideDirection
        >>> from vood import VElement, VElementGroup
        >>>
        >>> kf1, kf2 = slide_replace(
        ...     TextState(text="Before", x=100),
        ...     TextState(text="After", x=100),
        ...     direction=SlideDirection.LEFT,
        ...     distance=200
        ... )
        >>>
        >>> elem1 = VElement(text_renderer, keystates=kf1)
        >>> elem2 = VElement(text_renderer, keystates=kf2)
        >>> group = VElementGroup(elements=[elem1, elem2])
    """
    # Convert string to enum if needed
    if isinstance(direction, str):
        direction = SlideDirection(direction)

    half = duration / 2
    t_start = at_time - half
    t_end = at_time + half

    # Determine which property to animate and offsets
    direction_config = {
        SlideDirection.LEFT: ("x", -distance, distance),
        SlideDirection.RIGHT: ("x", distance, -distance),
        SlideDirection.UP: ("y", -distance, distance),
        SlideDirection.DOWN: ("y", distance, -distance),
    }

    prop, out_offset, in_offset = direction_config[direction]

    # Get original positions
    orig_pos_1 = getattr(state1, prop)
    orig_pos_2 = getattr(state2, prop)

    # Element 1: Slide out
    keyframes1 = [
        KeyState(time=t_start, state=replace(state1, opacity=1.0)),
        KeyState(
            time=t_end,
            state=replace(state1, **{prop: orig_pos_1 + out_offset}, opacity=0.0),
        ),
    ]

    # Element 2: Slide in (from opposite direction)
    keyframes2 = [
        KeyState(
            time=t_start,
            state=replace(state2, **{prop: orig_pos_2 + in_offset}, opacity=0.0),
        ),
        KeyState(time=t_end, state=replace(state2, **{prop: orig_pos_2}, opacity=1.0)),
    ]

    if extend_timeline:
        keyframes1 = [
            KeyState(time=0.0, state=replace(state1, opacity=1.0)),
            *keyframes1,
        ]
        keyframes2 = [
            *keyframes2,
            KeyState(time=1.0, state=replace(state2, opacity=1.0)),
        ]

    return keyframes1, keyframes2
