"""Ellipse renderer implementation using new architecture"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

import drawsvg as dw

from .base import Renderer
from vood.utils import to_rgb_string

from vood.components.states import EllipseState


class EllipseRenderer(Renderer):
    """Renderer class for rendering ellipse elements"""

    def __init__(self) -> None:
        """Initialize ellipse renderer

        No parameters needed - all properties come from the state
        """
        pass

    def _render_core(self, state: EllipseState) -> dw.Ellipse:
        """Render the ellipse renderer (geometry only) with the given state

        Returns:
            drawsvg Ellipse object
        """
        fill_color = to_rgb_string(state.color)

        # Create ellipse centered at origin with scaled radii
        ellipse_kwargs = {
            "cx": 0,
            "cy": 0,
            "rx": state.rx,
            "ry": state.ry,
            "fill": fill_color,
        }

        # Add stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            ellipse_kwargs["stroke"] = to_rgb_string(state.stroke_color)
            ellipse_kwargs["stroke_width"] = state.stroke_width

        return dw.Ellipse(**ellipse_kwargs)
