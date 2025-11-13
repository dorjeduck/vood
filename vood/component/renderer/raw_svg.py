from typing import Optional
from dataclasses import dataclass
from .base import Renderer
import drawsvg as dw

from ..state.raw_svg import RawSvgState


class RawSvgRenderer(Renderer):
    """
    Renderer that renders raw SVG data.
    """

    def _render_core(self, state: RawSvgState, drawing: Optional[dw.Drawing] = None) -> dw.Raw:
        # Render the raw SVG data as a drawsvg element
        return dw.Raw(state.svg_data)
