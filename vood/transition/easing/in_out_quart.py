def in_out_quart(t: float) -> float:
    """Quartic ease in-out - dramatic acceleration and deceleration

    Combines strong ease-in with strong ease-out for very dramatic effect.
    Much more pronounced than quadratic in-out. Creates powerful, cinematic
    movement patterns.

    Use cases:
    - Cinematic camera movements
    - Dramatic scene transitions
    - Hero element animations
    - High-impact visual effects

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) / 2
