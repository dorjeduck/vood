from __future__ import annotations

import drawsvg as dw

from vood.components.renderer.base import Renderer
from vood.components.states.morph_base import MorphBaseState


class MorphRenderer(Renderer):
    """Renderer for morphable geometric shapes

    Handles both open and closed shapes, with special logic for fill behavior.
    """

    def _render_core(self, state: MorphBaseState) -> dw.Group:
        """Render the morphable shape"""
        vertices = state.get_vertices()

        # Flatten vertices for drawsvg
        coords = [coord for x, y in vertices for coord in (x, y)]

        group = dw.Group()

        # Get colors if they exist
        fill_color = getattr(state, "fill_color", None)
        stroke_color = getattr(state, "stroke_color", None)
        stroke_width = getattr(state, "stroke_width", 0)

        # Build rendering kwargs
        lines_kwargs = {}

        # Fill handling (Manim-style)
        if state.closed and fill_color:
            # Closed shape with fill color
            lines_kwargs["fill"] = fill_color.to_rgb_string()
            lines_kwargs["close"] = True
        elif not state.closed and fill_color and fill_color.a > 0:
            # Open shape morphing into closed: show fill but don't close stroke
            # This creates the "ghost connection" for fill area

            # Draw fill area first (closed)
            fill_lines = dw.Lines(
                *coords, fill=fill_color.to_rgb_string(), stroke="none", close=True
            )
            group.append(fill_lines)

            # Then draw stroke without closing
            if stroke_color and stroke_width > 0:
                stroke_lines = dw.Lines(
                    *coords,
                    fill="none",
                    stroke=stroke_color.to_rgb_string(),
                    stroke_width=stroke_width,
                    close=False,
                )
                group.append(stroke_lines)
            return group
        else:
            # No fill
            lines_kwargs["fill"] = "none"
            lines_kwargs["close"] = state.closed

        # Stroke handling
        if stroke_color and stroke_width > 0:
            lines_kwargs["stroke"] = stroke_color.to_rgb_string()
            lines_kwargs["stroke_width"] = stroke_width

        # Create the shape
        lines = dw.Lines(*coords, **lines_kwargs)
        group.append(lines)

        return group
