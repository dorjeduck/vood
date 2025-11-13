def out_expo(t: float) -> float:
    """Exponential ease out - rapid start, then very slow end"""
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 1 if t == 1 else 1 - pow(2, -10 * t)
