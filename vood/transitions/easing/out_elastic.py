def out_elastic(t: float) -> float:
    """
    Elastic ease out - like a rubber band snapping into place with bouncy overshoot.

    Creates rapid initial movement toward the target, then oscillates around the final
    position with decreasing amplitude until settling. The elastic effect makes arrivals
    feel lively and energetic rather than mechanical.

    Mathematical form: Uses 2^(-10t) * sin(t * 2π/3) + 1 for damped oscillation

    Use cases:
    - UI elements appearing with playful character
    - Button press feedback that feels responsive and alive
    - Modal dialogs or menus that bounce into view
    - Success animations that celebrate completion
    - Dropdown menus with personality
    - Game UI elements that need bounce and appeal

    Like a rubber ball dropped on the ground: quick fall to the surface,
    then several smaller bounces before coming to rest.

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
    c4 = (2 * math.pi) / 3
    return pow(2, -10 * t) * math.sin(t * c4 - c4) + 1
