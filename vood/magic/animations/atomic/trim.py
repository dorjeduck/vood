# ============================================================================
# vood/animations/atomic/fade.py
# ============================================================================
"""Fade out, switch, fade in animation"""

from typing import List, Tuple
from dataclasses import replace
from vood.components import State


def trim(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.2,
    extend_timeline: bool = False,
) -> List[Tuple[float, State]]:
    
    half = duration / 2
    t_start = at_time - half
    t_end = at_time + half

    keyframes = [
        (t_start, state1),
        (t_end, state2),
    ]

    if extend_timeline:
        keyframes = [
            (0.0, state1),
            *keyframes,
            (1.0, state2),
        ]

    return keyframes
