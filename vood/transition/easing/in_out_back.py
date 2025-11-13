def in_out_back(t: float) -> float:
    """Back ease in-out - pulls back, overshoots, then settles

    Combines anticipation with overshoot. Pulls back at the start, then
    overshoots at the end before settling. Creates maximum personality
    and life in animations.

    Use cases:
    - Hero element animations
    - Playful, character-driven interfaces
    - When you want maximum personality
    - Spring-loaded mechanisms

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value with both anticipation and overshoot

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    c1 = 1.70158
    c2 = c1 * 1.525
    if t < 0.5:
        return (pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
    else:
        return (pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2
