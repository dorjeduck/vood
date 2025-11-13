from typing import Any


def step(start: Any, end: Any, t: float) -> Any:
    """Step interpolation: returns start if t<0.5 else end"""
    return start if t < 0.5 else end
