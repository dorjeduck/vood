# ============================================================================
# vood/animations/atomic/rotate.py
# ============================================================================
"""Rotate out, switch, rotate in animation"""

from typing import List, Tuple
from dataclasses import replace
from vood.component import State


def rotate(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.3,
    angle: float = 360,
    extend_timeline: bool = False,
) -> List[Tuple[float, State]]:
    """Rotate out first state, switch properties, rotate in second state

    Element rotates while fading out, properties change, then rotates
    back while fading in. Creates a spinning transition effect.

    Args:
        state1: Starting state (will rotate out)
        state2: Ending state (will rotate in)
        at_time: Center point of the transition (0.0 to 1.0)
        duration: Total duration of rotate out + rotate in (0.0 to 1.0)
        angle: Rotation angle in degrees (360 = full rotation)
        extend_timeline: If True, adds keystates at 0.0 and 1.0 to cover full timeline

    Returns:
        List of keystates for single element

    Example:
        >>> from vood.animations.atomic import rotate
        >>>
        >>> # Element only exists during rotation (partial timeline)
        >>> keystates = rotate(
        ...     TextState(text="Before", rotation=0),
        ...     TextState(text="After", rotation=0),
        ...     at_time=0.5,
        ...     angle=180
        ... )
        >>> element = VElement(renderer, keystates=keystates)
    """
    half = duration / 2
    t_start = at_time - half
    t_end = at_time + half

    # Get original rotations
    orig_rot_1 = getattr(state1, "rotation", 0)
    orig_rot_2 = getattr(state2, "rotation", 0)

    keystates = [
        (t_start, replace(state1, rotation=orig_rot_1, opacity=1.0)),
        (
            at_time,
            replace(state1, rotation=orig_rot_1 + angle, opacity=0.0),
        ),  # Rotated out
        (
            at_time,
            replace(state2, rotation=orig_rot_2 - angle, opacity=0.0),
        ),  # Switch (rotated)
        (t_end, replace(state2, rotation=orig_rot_2, opacity=1.0)),  # Rotated in
    ]

    if extend_timeline:
        keystates = [
            (0.0, replace(state1, rotation=orig_rot_1, opacity=1.0)),
            *keystates,
            (1.0, replace(state2, rotation=orig_rot_2)),
        ]

    return keystates
