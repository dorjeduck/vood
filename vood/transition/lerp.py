from typing import Union

Number = Union[int, float]


def lerp(start: Number, end: Number, t: float) -> float:
    """Linear interpolation between start and end values.

    Performs standard linear interpolation: lerp(a, b, t) = a + (b - a) * t

    Args:
        start: Starting value (int or float)
        end: Ending value (int or float)
        t: Interpolation parameter (0.0 to 1.0)
           - t=0.0 returns start
           - t=1.0 returns end
           - t=0.5 returns midpoint

    Returns:
        Interpolated value as float

    Examples:
        >>> lerp(0, 100, 0.5)
        50.0
        >>> lerp(10, 20, 0.25)
        12.5
        >>> lerp(-10, 10, 0.75)
        5.0

    Note:
        Values of t outside [0, 1] are allowed and will extrapolate.
    """
    return start + (end - start) * t
