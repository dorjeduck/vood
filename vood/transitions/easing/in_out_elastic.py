def in_out_elastic(t: float) -> float:
    """
    Elastic ease in-out - combines elastic anticipation with bouncy arrival.

    Creates a complex motion that starts with oscillating buildup (like drawing back
    a slingshot), rapidly accelerates through the middle, then oscillates around
    the target before settling. Combines the best of both elastic behaviors.

    Mathematical form: Uses scaled sine waves with exponential decay on both ends

    Use cases:
    - High-impact transitions that need maximum personality
    - Game animations for special abilities or power-ups
    - Attention-grabbing modal transitions
    - Playful loading sequences that entertain users
    - Celebration animations that feel extra bouncy
    - UI elements that need to stand out with elastic character

    Like a professional yo-yo trick: complex wind-up with multiple oscillations,
    rapid motion through the middle, then multiple bounces before settling perfectly.

    Args:
        t: Time factor between 0.0 and 1.0

    Returns:
        Eased value between 0.0 and 1.0

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    import math

    if t == 0:
        return 0
    if t == 1:
        return 1
    c5 = (2 * math.pi) / 4.5
    if t < 0.5:
        return -(pow(2, 20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
    else:
        return (pow(2, -20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1
