def in_out_sine(t: float) -> float:
    """Sine ease in-out - perfectly smooth, natural curve

    Based on a half sine wave. Creates the smoothest possible curve for
    in-out animations. No sharp transitions, completely organic feeling.
    Often preferred for subtle, elegant animations.

    Use cases:
    - Elegant UI animations
    - Smooth property changes
    - Natural breathing effects
    - When smoothness is paramount

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1, following -(cos(π*t)-1)/2

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    import math

    return -(math.cos(math.pi * t) - 1) / 2
