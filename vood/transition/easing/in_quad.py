def in_quad(t: float) -> float:
    """Quadratic ease in - slow start, accelerating

    Creates a gentle acceleration from rest. The animation starts very slowly
    and gradually speeds up. Perfect for objects starting to move or fade in.

    Use cases:
    - Elements appearing/growing from nothing
    - Objects starting to move from rest
    - Gentle fade-ins

    Args:
        t: Time factor between 0 and 1

    Returns:
        Eased value between 0 and 1, following t²

    Raises:
        ValueError: If t is not between 0 and 1
    """
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return t * t
