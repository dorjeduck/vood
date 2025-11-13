from typing import List, Tuple, Callable, Any
from vood.component import State


# Type for any atomic transition function
AtomicTransitionFunc = Callable[..., List[Tuple[float, State]]]


def sequential_transition(
    states: List[State],
    transition_func: AtomicTransitionFunc,
    transition_factor: float,
    **transition_kwargs: Any,
) -> List[Tuple[float, State]]:
    """
    Applies an atomic transition function sequentially across a list of states,
    centering transitions on the midpoints between states across the [0.0, 1.0] timeline.

    Args:
        states: List of states to transition between (must have at least 2).
        transition_func: The atomic transition function (must return List[Tuple[float, State]]).
        transition_factor: A factor (0.0 to 1.0) applied to the segment_unit to
                          determine the transition duration.
        **transition_kwargs: Additional keyword arguments to pass to the transition function
                           (e.g., extend_timeline=False, angle=180, direction="left", etc.)

    Returns:
        List of keystates for a single element covering the full 0.0 to 1.0 timeline.

    Example:
        >>> from vood.animations.atomic import fade, rotate, slide
        >>> from vood.animations.atomic.slide import SlideDirection
        >>>
        >>> # Simple fade sequence
        >>> keystates = sequential_transition(
        ...     keystates=[state1, state2, state3],
        ...     transition_func=fade,
        ...     transition_factor=0.5
        ... )
        >>>
        >>> # Rotate sequence with custom angle
        >>> keystates = sequential_transition(
        ...     keystates=[state1, state2, state3],
        ...     transition_func=rotate,
        ...     transition_factor=0.6,
        ...     angle=270
        ... )
        >>>
        >>> # Slide sequence with direction
        >>> keystates = sequential_transition(
        ...     keystates=[state1, state2, state3, state4],
        ...     transition_func=slide,
        ...     transition_factor=0.7,
        ...     direction=SlideDirection.LEFT,
        ...     distance=150
        ... )
    """
    if len(states) < 2:
        if len(states) == 1:
            return [(0.0, states[0]), (1.0, states[0])]
        return []

    num_transitions = len(states) - 1

    # Calculate time unit based on twice the number of transitions to find midpoints
    time_denominator = 2 * num_transitions

    # Calculate the actual transition duration based on the factor
    segment_unit = 1.0 / num_transitions
    transition_duration = segment_unit * transition_factor

    all_keyframes: List[Tuple[float, State]] = []

    # 1. Add the initial keystate at 0.0
    all_keyframes.append((0.0, states[0]))

    # 2. Iterate through all N-1 transitions
    for i in range(num_transitions):
        state1 = states[i]
        state2 = states[i + 1]

        # Calculate center time using the midpoint formula: (2i + 1) / (2 * N-1)
        at_time = (2 * i + 1) / time_denominator

        # 3. Call the atomic transition function with additional kwargs
        transition_keyframes = transition_func(
            state1=state1,
            state2=state2,
            at_time=at_time,
            duration=transition_duration,
            **transition_kwargs,  # Pass through all extra parameters
        )

        all_keyframes.extend(transition_keyframes)

    # 4. Add the final keystate at 1.0
    all_keyframes.append((1.0, states[-1]))

    # 5. Clean up, sort, and clamp all keystate times to [0.0, 1.0]
    unique_keyframes = {}
    for t_raw, state in all_keyframes:
        # Clamp the time to ensure it is in [0.0, 1.0]
        t = max(0.0, min(1.0, t_raw))
        unique_keyframes[t] = state

    final_keyframes = sorted(unique_keyframes.items(), key=lambda item: item[0])

    return final_keyframes
