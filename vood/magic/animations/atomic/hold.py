from typing import List, Tuple

from vood.components import State


def hold(
    states: List[State],
    hold_factor: float = 0.5,
) -> List[Tuple[float, State]]:
    """Add hold periods at segment boundaries for a list of states

    Divides timeline into equal segments and adds holds at the start/end of each.
    The hold_factor controls what fraction of each segment is spent holding vs transitioning.

    Args:
        states: List of states to distribute across timeline
        hold_factor: Fraction of each segment to use for holds (0.0 to 1.0)
                    0.5 means half the segment is holds, half is transition

    Returns:
        List of keyframes with hold periods at segment boundaries

    Example:
        >>> with_hold_boundaries([s1, s2, s3], hold_factor=0.5)
        # Creates holds at start of s1, around s1-s2 boundary, around s2-s3 boundary, at end of s3
    """
    if len(states) < 2:
        if len(states) == 1:
            return [(0.0, states[0]), (1.0, states[0])]
        return []

    seg_time = 1.0 / (len(states) - 1)
    hht = hold_factor * seg_time / 2  # half hold time

    keyframes = []

    # First state
    keyframes.append((0.0, states[0]))
    keyframes.append((hht, states[0]))

    # Middle states
    for i in range(1, len(states) - 1):
        t = i * seg_time
        keyframes.append((t - hht, states[i]))
        keyframes.append((t + hht, states[i]))

    # Last state
    t_last = (len(states) - 1) * seg_time
    keyframes.append((t_last - hht, states[-1]))
    keyframes.append((1.0, states[-1]))

    return keyframes
