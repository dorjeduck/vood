def in_out(t: float) -> float:
    """Smooth ease in and out using quadratic curve

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return t * t * (3 - 2 * t)
