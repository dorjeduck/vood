def out_bounce(t: float) -> float:
    """
    Bounce ease out - like a ball bouncing to a stop with realistic physics.

    Creates the classic bouncing ball effect with mathematically accurate bounce
    timing and heights. Each bounce is smaller than the last, following realistic
    physics until the motion settles at the target position.

    Mathematical form: Uses piecewise function with 7.5625 coefficient for realistic bounce

    Use cases:
    - Classic bouncing ball animations
    - UI elements dropping into place naturally
    - Success notifications that bounce to celebrate
    - Drag-and-drop feedback with satisfying landing
    - Menu items bouncing into view
    - Any animation that needs playful, physics-based character

    Like dropping a rubber ball: quick fall, then several decreasing bounces
    (big bounce, medium bounce, small bounce) before settling on the ground.

    Args:
        t: Time factor between 0.0 and 1.0

    Returns:
        Eased value between 0.0 and 1.0

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375
