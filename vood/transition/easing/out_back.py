def out_back(t: float) -> float:
    """Back ease out - overshoots then settles back

    Shoots past the target and then settles back into place. Like a spring
    that compresses too far and bounces back. Creates satisfying overshoot
    effects that feel dynamic and alive.

    Use cases:
    - Elements settling into place with overshoot
    - Spring-like animations
    - Satisfying button feedback
    - Objects that "land" with impact

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value that overshoots past 1 before settling

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
