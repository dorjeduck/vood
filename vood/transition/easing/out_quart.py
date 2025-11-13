def out_quart(t: float) -> float:
    """Quartic ease out - very fast start with strong deceleration

    Starts very rapidly and then decelerates strongly to a gentle stop.
    More dramatic than quadratic ease-out. Great for impactful arrivals.

    Use cases:
    - Elements slamming into place then settling
    - Dramatic slide-ins
    - Impact animations
    - Strong emphasis on arrival

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1, following 1-(1-t)⁴

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 1 - pow(1 - t, 4)
