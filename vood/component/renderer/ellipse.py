"""Ellipse renderer implementation using new architecture"""

from __future__ import annotations
from typing import Optional

import drawsvg as dw

from .base import Renderer
from ..registry import register_renderer
from ..state.ellipse import EllipseState


@register_renderer(EllipseState)
class EllipseRenderer(Renderer):
    """Renderer class for rendering ellipse elements"""

    def __init__(self) -> None:
        """Initialize ellipse renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(self, state: EllipseState, drawing: Optional[dw.Drawing] = None) -> dw.Ellipse:
        """Render the ellipse renderer (geometry only) with the given state

        Returns:
            drawsvg Ellipse object
        """

        # Create ellipse centered at origin with scaled radii
        ellipse_kwargs = {
            "cx": 0,
            "cy": 0,
            "rx": state.rx,
            "ry": state.ry,
            "fill": state.fill_color.to_rgb_string(),
            "fill_opacity": state.fill_opacity,
        }

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            ellipse_kwargs["stroke"] = state.stroke_color.to_rgb_string()
            ellipse_kwargs["stroke_width"] = state.stroke_width
            ellipse_kwargs["stroke_opacity"] = state.stroke_opacity

        return dw.Ellipse(**ellipse_kwargs)
