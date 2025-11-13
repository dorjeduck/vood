def out_quad(t: float) -> float:
    """Quadratic ease out - fast start, decelerating

    Starts fast and gradually slows down to a gentle stop. Creates a natural
    feeling deceleration, like an object coming to rest.

    Use cases:
    - Elements settling into place
    - Objects coming to a stop
    - Gentle fade-outs
    - UI elements sliding into final position

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1, following 1-(1-t)²

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 1 - (1 - t) * (1 - t)
