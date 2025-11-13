# ============================================================================
# vood/animations/atomic/slide.py
# ============================================================================
"""Slide out, switch, slide in animation"""

from typing import List, Tuple, Union
from dataclasses import replace
from vood.component import State
from ..enums import SlideDirection


def slide(
    state1: State,
    state2: State,
    at_time: float = 0.5,
    duration: float = 0.3,
    direction: Union[SlideDirection, str] = SlideDirection.LEFT,
    distance: float = 100,
    extend_timeline: bool = False,
) -> List[Tuple[float, State]]:
    """Slide out first state, switch properties, slide in second state

    Element slides off-screen in one direction, properties change, then
    slides back in from the opposite direction.

    Args:
        state1: Starting state (will slide out)
        state2: Ending state (will slide in)
        at_time: Center point of the transition (0.0 to 1.0)
        duration: Total duration of slide out + slide in (0.0 to 1.0)
        direction: Direction to slide out (SlideDirection enum or string)
        distance: Distance to slide in pixels
        extend_timeline: If True, adds keystates at 0.0 and 1.0 to cover full timeline

    Returns:
        List of keystates for single element

    Example:
        >>> from vood.animations.atomic import slide, SlideDirection
        >>>
        >>> # Element only exists during slide (partial timeline)
        >>> keystates = slide(
        ...     TextState(text="Before", x=100),
        ...     TextState(text="After", x=100),
        ...     direction=SlideDirection.LEFT,
        ...     distance=200
        ... )
        >>> element = VElement(renderer, keystates=keystates)
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

    keystates = [
        (t_start, state1),
        (
            at_time,
            replace(state1, **{prop: orig_pos_1 + out_offset}, opacity=0.0),
        ),  # Slid out
        (
            at_time,
            replace(state2, **{prop: orig_pos_2 + in_offset}, opacity=0.0),
        ),  # Switch (off-screen)
        (t_end, replace(state2, **{prop: orig_pos_2}, opacity=1.0)),  # Slid in
    ]

    if extend_timeline:
        keystates = [
            (0.0, state1),
            *keystates,
            (1.0, state2),
        ]

    return keystates
