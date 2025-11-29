from dataclasses import dataclass
from .base import State
from vood.component.registry import renderer
from vood.component.renderer.raw_svg import RawSvgRenderer


@renderer(RawSvgRenderer)
@dataclass(frozen=True)
class RawSvgState(State):
    """
    State for raw SVG data rendering.
    """

    svg_data: str = ""

