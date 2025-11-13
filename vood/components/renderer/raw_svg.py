from dataclasses import dataclass
from .base import State, Renderer
import drawsvg as dw

from vood.components.states import RawSvgState


class RawSvgRenderer(Renderer):
    """
    Renderer that renders raw SVG data.
    """

    def _render_core(self, state: RawSvgState) -> dw.Raw:
        # Render the raw SVG data as a drawsvg element
        return dw.Raw(state.svg_data)
