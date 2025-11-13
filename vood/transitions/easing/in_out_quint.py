def in_out_quint(t: float) -> float:
    """Quintic ease in-out - maximum drama with smooth transition

    The most extreme version of ease in-out. Combines explosive acceleration
    with explosive deceleration for maximum visual impact while maintaining
    smooth transitions.

    Use cases:
    - Epic cinematic movements
    - Maximum impact transitions
    - Hero moments in animations
    - When you need the most dramatic curve possible

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 16 * t * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 5) / 2
