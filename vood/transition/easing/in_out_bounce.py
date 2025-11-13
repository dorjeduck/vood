def in_out_bounce(t: float) -> float:
    """
    Bounce ease in-out - bounces at both start and end with smooth middle transition.

    Combines bounce-in and bounce-out effects, creating complex motion that bounces
    at the beginning (building energy), smoothly transitions through the middle,
    then bounces at the end (settling into place). Maximum playful character.

    Mathematical form: Uses bounce-in for first half, bounce-out for second half

    Use cases:
    - Maximum impact transitions between major interface states
    - Game animations that need extra personality and fun
    - Celebration sequences that feel extra bouncy and joyful
    - Loading animations that entertain with complex bouncing
    - Special effect transitions that need to stand out
    - UI elements that should feel extremely playful and engaging

    Like a rubber ball in a pinball machine: bounces off the starting bumper,
    flies through the middle space, then bounces several times before settling
    in the target slot.

    Args:
        t: Time factor between 0.0 and 1.0

    Returns:
        Eased value between 0.0 and 1.0

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")

    # Import bounce functions from the same directory
    from .out_bounce import out_bounce

    if t < 0.5:
        return (1 - out_bounce(1 - 2 * t)) / 2
    else:
        return (1 + out_bounce(2 * t - 1)) / 2
