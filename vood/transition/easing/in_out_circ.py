def in_out_circ(t: float) -> float:
    """
    Circular ease in-out - smooth acceleration following circular arc, then smooth deceleration.

    Combines circular ease-in and ease-out, creating a perfectly smooth S-curve that follows
    the mathematical properties of a circle. The acceleration and deceleration phases are
    perfectly symmetrical and create very natural-feeling motion.

    Mathematical form: Uses √(1-t²) for circular arc calculation

    Use cases:
    - Natural object motion that needs to feel physically realistic
    - Smooth camera movements and panning
    - Organic transitions between interface states
    - Animations where you want smooth acceleration without harsh stops
    - Breathing or pulsing effects
    - Element positioning that should feel effortless

    Like a skilled driver: smooth acceleration onto a highway, maintaining steady speed,
    then smooth deceleration to a perfect parking position.

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

    if t < 0.5:
        return (1 - math.sqrt(1 - pow(2 * t, 2))) / 2
    else:
        return (math.sqrt(1 - pow(-2 * t + 2, 2)) + 1) / 2
