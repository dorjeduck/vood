# ============================================================================
# vood/animations/atomic/scale.py
# ============================================================================
"""Scale down, switch, scale up animation"""

from typing import List, Tuple
from dataclasses import replace
from vood.component import State


def scale(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.3,
    min_scale: float = 0.0,
    extend_timeline: bool = False,
) -> List[Tuple[float, State]]:
    """Scale down first state, switch properties, scale up second state

    Element scales down to minimum (typically 0), properties change,
    then scales back up. Creates a "shrink and grow" effect.

    Args:
        state1: Starting state (will scale down)
        state2: Ending state (will scale up)
        at_time: Center point of the transition (0.0 to 1.0)
        duration: Total duration of scale down + scale up (0.0 to 1.0)
        min_scale: Minimum scale value (0.0 = invisible, 1.0 = no change)
        extend_timeline: If True, adds keystates at 0.0 and 1.0 to cover full timeline

    Returns:
        List of keystates for single element

    Example:
        >>> from vood.animations.atomic import scale
        >>>
        >>> # Element only exists during scale (partial timeline)
        >>> keystates = scale(
        ...     CircleState(radius=50),
        ...     CircleState(radius=50, fill=(255, 0, 0)),
        ...     at_time=0.5,
        ...     min_scale=0.0
        ... )
        >>> element = VElement(renderer, keystates=keystates)
    """
    half = duration / 2
    t_start = at_time - half
    t_end = at_time + half

    keystates = [
        (t_start, replace(state1, scale=1.0)),
        (at_time, replace(state1, scale=min_scale, opacity=0.0)),  # Scaled down
        (at_time, replace(state2, scale=min_scale, opacity=0.0)),  # Switch (tiny)
        (t_end, replace(state2, scale=1.0, opacity=1.0)),  # Scaled up
    ]

    if extend_timeline:
        keystates = [
            (0.0, replace(state1, scale=1.0)),
            *keystates,
            (1.0, replace(state2, scale=1.0)),
        ]

    return keystates
