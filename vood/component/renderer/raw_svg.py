from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass
from .base import Renderer

if TYPE_CHECKING:
    from ..state.raw_svg import RawSvgState

import drawsvg as dw



class RawSvgRenderer(Renderer):
    """
    Renderer that renders raw SVG data.
    """

    def _render_core(
        self, state: "RawSvgState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Raw:
        # Render the raw SVG data as a drawsvg element
        return dw.Raw(state.svg_data)
