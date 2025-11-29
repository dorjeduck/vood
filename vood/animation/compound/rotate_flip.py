# ============================================================================
# vood/animations/compound/rotate_flip.py
# ============================================================================
"""Rotate flip effect with two elements"""

from typing import Tuple
from dataclasses import replace
from vood.component import State
from vood.velement.keystate import KeyState, KeyStates

def rotate_flip(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.5,
    angle: float = 180,
    extend_timeline: bool = False,
) -> Tuple[KeyStates,KeyStates]:
    """Create a flip effect by rotating two elements

    First element rotates away while fading out, second element rotates
    in while fading in. Creates a card-flip or page-turn effect.

    Args:
        state1: Starting state (front of card)
        state2: Ending state (back of card)
        at_time: Center point of the flip (0.0 to 1.0)
        duration: Duration of the flip (0.0 to 1.0)
        angle: Rotation angle in degrees (180 = half rotation)
        extend_timeline: If True, adds keystates at 0.0 and 1.0 to cover full timeline

    Returns:
        Tuple of (element1_keyframes, element2_keyframes)

    Example:
        >>> from vood.animations.compound import rotate_flip
        >>> from vood import VElement, VElementGroup
        >>>
        >>> kf1, kf2 = rotate_flip(
        ...     TextState(text="Front", rotation=0),
        ...     TextState(text="Back", rotation=0),
        ...     at_time=0.5,
        ...     angle=180
        ... )
        >>>
        >>> elem1 = VElement(text_renderer, keystates=kf1)
        >>> elem2 = VElement(text_renderer, keystates=kf2)
        >>> group = VElementGroup(elements=[elem1, elem2])
    """
    half = duration / 2
    t_start = at_time - half
    t_mid = at_time
    t_end = at_time + half

    # Get original rotations
    orig_rot_1 = getattr(state1, "rotation", 0)
    orig_rot_2 = getattr(state2, "rotation", 0)

    # Element 1: Rotate and fade out (first half)
    keyframes1 = [
        KeyState(time=t_start, state=replace(state1, rotation=orig_rot_1, opacity=1.0)),
        KeyState(time=t_mid, state=replace(state1, rotation=orig_rot_1 + angle / 2, opacity=0.0)),
    ]

    # Element 2: Rotate and fade in (second half)
    keyframes2 = [
        KeyState(time=t_mid, state=replace(state2, rotation=orig_rot_2 - angle / 2, opacity=0.0)),
        KeyState(time=t_end, state=replace(state2, rotation=orig_rot_2, opacity=1.0)),
    ]

    if extend_timeline:
        keyframes1 = [
            KeyState(time=0.0, state=replace(state1, rotation=orig_rot_1, opacity=1.0)),
            *keyframes1,
        ]
        keyframes2 = [
            *keyframes2,
            KeyState(time=1.0, state=replace(state2, rotation=orig_rot_2, opacity=1.0)),
        ]

    return keyframes1, keyframes2
