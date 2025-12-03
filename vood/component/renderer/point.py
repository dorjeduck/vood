"""Renderer for PointState - renders nothing"""

from __future__ import annotations
from typing import TYPE_CHECKING
import drawsvg as dw
from .base import Renderer

if TYPE_CHECKING:
    from ..state.point import PointState


class PointRenderer(Renderer):
    """Renderer for PointState that produces no visual output

    PointState represents a collapsed/degenerate shape used for explicit
    disappearance/appearance transitions. The renderer produces an empty
    group, making the shape invisible at t=1.0 while still participating
    in morphing transitions.

    Optionally, a debug marker can be enabled to visualize point locations
    during development.
    """

    def _render_core(self, state: "PointState", drawing=None) -> dw.Group:
        """Render nothing (empty group)

        Args:
            state: PointState to render
            drawing: Optional drawing context (unused)

        Returns:
            Empty group (no visual output)
        """
        # Return empty group - PointState renders nothing
        return dw.Group()

    # Optional: Add debug marker support if needed
    # def _render_core(self, state: "PointState", drawing=None) -> dw.Group:
    #     """Render debug marker (optional)"""
    #     group = dw.Group()
    #     if getattr(state, 'debug', False):
    #         # Small cross marker for debugging
    #         size = 5
    #         group.append(dw.Line(-size, 0, size, 0, stroke='red', stroke_width=1))
    #         group.append(dw.Line(0, -size, 0, size, stroke='red', stroke_width=1))
    #     return group
