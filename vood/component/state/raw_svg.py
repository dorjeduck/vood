from dataclasses import dataclass
from .base import State


@dataclass(frozen=True)
class RawSvgState(State):
    """
    State for raw SVG data rendering.
    """

    svg_data: str = ""

    @staticmethod
    def get_renderer_class():
        from ..renderer.raw_svg import RawSvgRenderer

        return RawSvgRenderer
