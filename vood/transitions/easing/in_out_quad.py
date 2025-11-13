def in_out_quad(t: float) -> float:
    """Quadratic ease in-out - accelerate then decelerate

    Combines the acceleration of ease-in with the deceleration of ease-out.
    Starts slowly, speeds up in the middle, then slows down at the end.
    Very natural feeling for most animations.

    Use cases:
    - General purpose smooth animations
    - Position changes that should feel natural
    - Size transitions
    - Most UI animations

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
