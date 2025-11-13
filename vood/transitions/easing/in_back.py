def in_back(t: float) -> float:
    """Back ease in - pulls back before moving forward

    Creates an anticipation effect by briefly moving in the opposite direction
    before accelerating toward the target. Like pulling back a slingshot or
    winding up before throwing. Adds personality and life to animations.

    Use cases:
    - UI elements that "wind up" before appearing
    - Character animations with anticipation
    - Playful button interactions
    - Adding personality to mechanical movements

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value that goes slightly negative before reaching 1

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t
