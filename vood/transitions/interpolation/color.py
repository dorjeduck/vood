from typing import Tuple, Union
from .lerp import lerp

Number = Union[int, float]
Color = Tuple[int, int, int]


def color(start: Color, end: Color, t: float) -> Color:
    """Interpolate between RGB colors"""
    r = int(lerp(start[0], end[0], t))
    g = int(lerp(start[1], end[1], t))
    b = int(lerp(start[2], end[2], t))
    return (r, g, b)
