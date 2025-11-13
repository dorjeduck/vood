def in_out_cubic(t: float) -> float:
    """Smooth cubic easing, combining in and out effects

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
