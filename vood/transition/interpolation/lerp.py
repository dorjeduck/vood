from typing import Union

Number = Union[int, float]


def lerp(start: Number, end: Number, t: float) -> Number:
    """Linear interpolation between start and end values"""
    return start + (end - start) * t
