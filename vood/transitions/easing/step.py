def step(t: float) -> float:
    """Step easing - instant change at 0.5

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 0 if t < 0.5 else 1
