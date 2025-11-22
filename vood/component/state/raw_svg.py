from dataclasses import dataclass
from .base import State


@dataclass(frozen=True)
class RawSvgState(State):
    """
    State for raw SVG data rendering.
    """

    svg_data: str = ""

