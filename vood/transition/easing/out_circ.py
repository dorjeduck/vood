def out_circ(t: float) -> float:
    """Circular ease out - fast start following circular arc"""
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    import math

    return math.sqrt(1 - pow(t - 1, 2))
