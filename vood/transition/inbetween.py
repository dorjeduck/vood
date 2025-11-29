from typing import List, Union

Number = Union[int, float]


def inbetween(start: Number, end: Number, num: int) -> List[float]:
    """Generate evenly-spaced values between start and end (exclusive).

    Creates a list of interpolated values between start and end, excluding
    the endpoints. Useful for generating intermediate animation frames or
    subdividing ranges.

    Args:
        start: Starting value (excluded from result)
        end: Ending value (excluded from result)
        num: Number of intermediate values to generate (must be >= 0)

    Returns:
        List of evenly-spaced float values between start and end

    Examples:
        >>> inbetween(0, 10, 1)
        [5.0]
        >>> inbetween(0, 10, 4)
        [2.0, 4.0, 6.0, 8.0]
        >>> inbetween(0, 1, 3)
        [0.25, 0.5, 0.75]
        >>> inbetween(0, 10, 0)
        []

    Note:
        To include endpoints, use numpy.linspace or manually add them:
        [start] + inbetween(start, end, num) + [end]
    """
    if num < 0:
        raise ValueError(f"num must be non-negative, got {num}")

    if num == 0:
        return []

    step = (end - start) / (num + 1)
    return [start + step * (i + 1) for i in range(num)]
