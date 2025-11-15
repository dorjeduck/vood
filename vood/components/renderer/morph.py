from __future__ import annotations


import drawsvg as dw


from vood.components.renderer.base import Renderer
from vood.components.states.morph_base import MorphBaseState


class MorphRenderer(Renderer):
    """Renderer for morphable geometric shapes

    Handles both open and closed shapes, with special logic for fill behavior:
    - Open shapes (lines): No fill, only stroke
    - Closed shapes: Both fill and stroke
    - During morphing: Fill fades in/out smoothly

    The key Manim-inspired feature: when morphing from open to closed,
    we implicitly connect the endpoints for fill determination without
    drawing that connecting line.
    """

    def _render_core(self, state: MorphBaseState) -> dw.Group:
        """Render the morphable shape

        Args:
            state: MorphState containing shape parameters

        Returns:
            drawsvg Group containing the rendered shape
        """
        vertices = state.get_vertices()

        # Flatten vertices for drawsvg
        coords = [coord for x, y in vertices for coord in (x, y)]

        group = dw.Group()

        # Build rendering kwargs
        lines_kwargs = {}

        # Fill handling (Manim-style)
        if state.closed and state.fill_color:
            # Closed shape with fill color
            lines_kwargs["fill"] = state.fill_color.to_rgb_string()
            lines_kwargs["close"] = True
        elif not state.closed and state.fill_color and state.fill_color.a > 0:
            # Open shape morphing into closed: show fill but don't close stroke
            # This creates the "ghost connection" for fill area
            lines_kwargs["fill"] = state.fill_color.to_rgb_string()
            lines_kwargs["close"] = True  # Close for fill only

            # We'll draw stroke separately without closing
        else:
            # No fill
            lines_kwargs["fill"] = "none"
            lines_kwargs["close"] = state.closed

        # Stroke handling
        if state.stroke_color and state.stroke_width > 0:
            stroke_color = state.stroke_color.to_rgb_string()

            if not state.closed and state.fill_color and state.fill_color.a > 0:
                # Special case: open shape with fill
                # Draw fill area first (closed)
                fill_lines = dw.Lines(
                    *coords,
                    fill=state.fill_color.to_rgb_string(),
                    stroke="none",
                    close=True,
                )
                group.append(fill_lines)

                # Then draw stroke without closing
                stroke_lines = dw.Lines(
                    *coords,
                    fill="none",
                    stroke=stroke_color,
                    stroke_width=state.stroke_width,
                    close=False,  # Don't close the stroke!
                )
                group.append(stroke_lines)
                return group
            else:
                # Normal stroke
                lines_kwargs["stroke"] = stroke_color
                lines_kwargs["stroke_width"] = state.stroke_width

        # Create the shape
        lines = dw.Lines(*coords, **lines_kwargs)
        group.append(lines)

        return group
