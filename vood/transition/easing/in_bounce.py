def in_bounce(t: float) -> float:
    """
    Bounce ease in - like a ball being thrown upward with decreasing bounces.

    Creates a bouncing motion that starts with several small bounces and builds
    toward the final movement. The effect simulates the reverse of a ball bouncing
    to a stop - instead bouncing with increasing energy toward the target.

    Mathematical form: Uses 1 - out_bounce(1-t) for reverse bounce calculation

    Use cases:
    - Elements that need to build energy before moving
    - Anticipation effects that suggest gathering momentum
    - Game mechanics for charging or powering up
    - UI elements that bounce into action
    - Loading animations that suggest building activity
    - Preparation phases before major transitions

    Like dribbling a basketball with increasing force: small bounces at first,
    building up to powerful movements toward the final position.

    Args:
        t: Time factor between 0.0 and 1.0

    Returns:
        Eased value between 0.0 and 1.0

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")

    # Import out_bounce function from the same directory
    from .out_bounce import out_bounce

    return 1 - out_bounce(1 - t)
