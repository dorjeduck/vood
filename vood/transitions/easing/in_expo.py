def in_expo(t: float) -> float:
    """Exponential ease in - very slow start, then rapid acceleration"""
    if not 0 <= t <= 1:
        raise ValueError("Time factor t must be between 0 and 1")
    return 0 if t == 0 else pow(2, 10 * (t - 1))
