def in_sine(t: float) -> float:
    """Sine ease in - gentle, natural acceleration

    Based on a quarter sine wave. Provides the most natural feeling
    acceleration - like how objects naturally speed up in the real world.
    Gentler than quadratic, more organic feeling.

    Use cases:
    - Natural object movements
    - Organic animations
    - Subtle fade-ins
    - When you want smooth but not too dramatic

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1, following 1-cos(t*π/2)

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    import math

    return 1 - math.cos((t * math.pi) / 2)
