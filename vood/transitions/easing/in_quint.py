def in_quint(t: float) -> float:
    """Quintic ease in - extremely slow start with explosive acceleration

    The most dramatic of the polynomial easing functions. Starts almost
    motionless and then explodes into rapid motion. Creates the strongest
    "build-up then release" effect.

    Use cases:
    - Explosive reveals
    - Maximum suspense building
    - Rocket launch animations
    - Extreme power-up effects

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1, following t⁵

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return t * t * t * t * t
