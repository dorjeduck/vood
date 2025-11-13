def out_sine(t: float) -> float:
    """Sine ease out - gentle, natural deceleration

    Based on a quarter sine wave. Provides the most natural feeling
    deceleration - like how objects naturally slow down in the real world.
    Perfect for organic, life-like movements.

    Use cases:
    - Natural settling animations
    - Organic fade-outs
    - Realistic physics simulations
    - Gentle UI transitions

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1, following sin(t*π/2)

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    import math

    return math.sin((t * math.pi) / 2)
