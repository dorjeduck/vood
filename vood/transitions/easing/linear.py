def linear(t: float) -> float:
    """Linear easing (no easing effect)

    Args:
        t: Time factor between 0 and 1

    Returns:
        Same value as input (t)

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return t
