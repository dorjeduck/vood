def in_quart(t: float) -> float:
    """Quartic ease in - very slow start with strong acceleration

    More dramatic than quadratic easing. Starts extremely slowly and then
    accelerates rapidly. Creates a strong "wind-up" effect.

    Use cases:
    - Dramatic entrances
    - Building suspense before rapid movement
    - Power-up animations
    - Loading animations that build momentum

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1, following t⁴

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return t * t * t * t
