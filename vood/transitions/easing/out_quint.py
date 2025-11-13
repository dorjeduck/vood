def out_quint(t: float) -> float:
    """Quintic ease out - explosive start with extreme deceleration

    Starts with maximum speed and then decelerates extremely strongly.
    Creates the most dramatic "impact then settle" effect of the polynomial
    functions.

    Use cases:
    - Maximum impact arrivals
    - Explosive entries that settle
    - Superhero landing effects
    - Heavy object animations

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1, following 1-(1-t)⁵

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 1 - pow(1 - t, 5)
