def in_out_expo(t: float) -> float:
    """
    Exponential ease in-out - slow start, dramatic acceleration, then dramatic deceleration.

    Combines exponential ease-in and ease-out, creating a smooth transition that starts slowly,
    accelerates dramatically in the middle, then decelerates dramatically to a smooth stop.
    The exponential nature creates very pronounced acceleration/deceleration phases.

    Mathematical form: Uses 2^(20t-10) for first half, 2^(-20t+10) for second half

    Use cases:
    - Cinematic zoom effects that need dramatic impact
    - High-energy transitions between major interface states
    - Emphasizing important state changes with theatrical timing
    - Creating "whoosh" effects in motion graphics
    - Scaling animations that need to feel powerful and impactful

    Like a sports car: gentle acceleration from standstill, then explosive power in the middle,
    followed by powerful braking to a smooth stop.

    Args:
        t: Time factor between 0.0 and 1.0

    Returns:
        Eased value between 0.0 and 1.0

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    if t == 0:
        return 0
    if t == 1:
        return 1
    if t < 0.5:
        return pow(2, 20 * t - 10) / 2
    else:
        return (2 - pow(2, -20 * t + 10)) / 2
