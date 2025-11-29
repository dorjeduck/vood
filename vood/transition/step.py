from typing import Any, TypeVar

T = TypeVar('T')


def step(start: T, end: T, t: float) -> T:
    """Step interpolation with instant transition at midpoint.

    This is a discrete interpolation function that switches from start to end
    at t=0.5, with no gradual transition. Used for non-numeric values that
    cannot be smoothly interpolated (e.g., strings, enums, objects).

    Args:
        start: Starting value of any type
        end: Ending value of any type
        t: Interpolation parameter (0.0 to 1.0)
           - t < 0.5 returns start
           - t >= 0.5 returns end

    Returns:
        Either start or end value (no intermediate values)

    Examples:
        >>> step("hello", "world", 0.3)
        'hello'
        >>> step("hello", "world", 0.5)
        'world'
        >>> step("hello", "world", 0.8)
        'world'
        >>> step(True, False, 0.49)
        True

    Note:
        The transition happens exactly at t=0.5 (inclusive of end).
    """
    return start if t < 0.5 else end
