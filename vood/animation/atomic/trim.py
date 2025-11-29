# ============================================================================
# vood/animations/atomic/fade.py
# ============================================================================
"""Fade out, switch, fade in animation"""

from vood.component import State
from vood.velement.keystate import KeyState, KeyStates


def trim(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.2,
    extend_timeline: bool = False,
) -> KeyStates:

    half = duration / 2
    t_start = at_time - half
    t_end = at_time + half

    keystates = [
        KeyState(time=t_start, state=state1),
        KeyState(time=t_end, state=state2),
    ]

    if extend_timeline:
        keystates = [
            KeyState(time=0.0, state=state1),
            *keystates,
            KeyState(time=1.0, state=state2),
        ]

    return keystates
