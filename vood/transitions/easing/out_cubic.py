def out_cubic(t: float) -> float:
    """Fast start, slow end using cubic curve

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 1 - pow(1 - t, 3)
