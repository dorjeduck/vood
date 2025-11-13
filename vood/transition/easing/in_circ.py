def in_circ(t: float) -> float:
    """Circular ease in - slow start following circular arc"""
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    import math

    return 1 - math.sqrt(1 - pow(t, 2))
