def in_elastic(t: float) -> float:
    """
    Elastic ease in - like pulling back a rubber band before release.

    Creates an oscillating motion that starts with small movements in the opposite direction,
    building tension before accelerating toward the target. The elastic effect creates a
    spring-like anticipation that makes the final movement feel more impactful.

    Mathematical form: Uses -2^(10(t-1)) * sin((t-1) * 2π/3) for oscillating decay

    Use cases:
    - UI elements that need playful, bouncy character
    - Attention-grabbing animations for buttons or notifications
    - Game mechanics that simulate elastic or spring-loaded objects
    - Anticipation effects before major actions
    - Cartoon-style animations that need exaggerated character
    - Loading animations that suggest building energy

    Like drawing back a slingshot: small backward movements building tension,
    then rapid acceleration toward the target with overshooting oscillation.

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
    return -pow(2, 10 * (t - 1)) * math.sin((t - 1) * c4 - c4)
