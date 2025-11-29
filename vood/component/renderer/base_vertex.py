"""Renderer for vertex-based shapes with multi-contour support"""

from __future__ import annotations
from typing import Optional
import drawsvg as dw

from vood.component.state.base_vertex import VertexState
from vood.component.renderer.base import Renderer
from vood.component.vertex import VertexContours


class VertexRenderer(Renderer):
    """Renderer for vertex-based shapes with multi-contour support

    Handles both open and closed shapes, with special logic for fill behavior:
    - Open shapes (lines): No fill, only stroke
    - Closed shapes: Both fill and stroke
    - Shapes with holes: Uses SVG masks for proper rendering during morphing
    - During morphing: Fill fades in/out smoothly

    The key Manim-inspired feature: when morphing from open to closed,
    we implicitly connect the endpoints for fill determination without
    drawing that connecting line.

    Hole rendering strategy:
    - Uses SVG masks (essential for morphing between different hole configurations)
    - Hole strokes rendered separately at normal width
    """

    def _render_core(
        self, state: VertexState, drawing: Optional[dw.Drawing] = None
    ) -> dw.Group:
        """Render the vertex-based shape

        Args:
            state: VertexState containing shape parameters
            drawing: Optional Drawing object for accessing defs section

        Returns:
            drawsvg Group containing the rendered shape
        """
        contours = state.get_contours()

        if not contours.outer.vertices:
            return dw.Group()

        group = dw.Group()

        # Get style properties
        fill_color = getattr(state, "fill_color", None)
        fill_opacity = getattr(state, "fill_opacity", 1)
        stroke_color = getattr(state, "stroke_color", None)
        stroke_opacity = getattr(state, "stroke_opacity", 1)
        stroke_width = getattr(state, "stroke_width", 0)

        holes_stroke_color = getattr(state, "holes_stroke_color", stroke_color)
        holes_stroke_opacity = getattr(state, "holes_stroke_opacity", stroke_opacity)
        holes_stroke_width = getattr(state, "holes_stroke_width", stroke_width)

        # Determine rendering strategy
        has_fill = fill_color and state.fill_opacity > 0
        has_stroke = stroke_color and stroke_width > 0 and state.stroke_opacity > 0

       
        # Check if vertices form a closed shape
        vertices_are_closed = self._check_closed(contours.outer.vertices)

        # Render based on whether we have holes
        if contours.has_holes:
            # Use mask-based rendering for shapes with holes
            self._render_with_holes(
                group,
                contours,
                has_fill,
                has_stroke,
                fill_color,
                fill_opacity,
                stroke_color,
                stroke_opacity,
                stroke_width,
                holes_stroke_color,
                holes_stroke_opacity,
                holes_stroke_width,
                state,
                drawing,
            )
        else:
            # Simple rendering for shapes without holes
            self._render_simple(
                group,
                contours.outer.vertices,
                vertices_are_closed,
                has_fill,
                has_stroke,
                fill_color,
                fill_opacity,
                stroke_color,
                stroke_opacity,
                stroke_width,
                state,
            )

        return group

    def _check_closed(self, vertices) -> bool:
        """Check if vertices form a closed shape"""
        if len(vertices) < 2:
            return False

        first_vertex = vertices[0]
        last_vertex = vertices[-1]
        
        
        distance = last_vertex.distance_to(first_vertex)
        
        return distance < 1.0  # Tolerance of 1 pixel

    def _render_simple(
        self,
        group,
        vertices,
        vertices_are_closed,
        has_fill,
        has_stroke,
        fill_color,
        fill_opacity,
        stroke_color,
        stroke_opacity,
        stroke_width,
        state,
    ):
        """Render a simple shape without holes"""
        first_vertex = vertices[0]

        # Render fill
        if has_fill:
            fill_path = dw.Path(
                fill=fill_color.to_rgb_string(),
                fill_opacity=fill_opacity,
                stroke="none",
            )

            fill_path.M(first_vertex.x, first_vertex.y)
            for v in vertices[1:]:
                fill_path.L(v.x, v.y)
            fill_path.Z()

            group.append(fill_path)

        # Render stroke
        if has_stroke:
            kwargs = {}
            if hasattr(state, "stroke_linecap") and state.stroke_linecap is not None:
                kwargs["stroke_linecap"] = state.stroke_linecap

            stroke_path = dw.Path(
                fill="none",
                stroke=stroke_color.to_rgb_string(),
                stroke_opacity=stroke_opacity,
                stroke_width=stroke_width,
                **kwargs,
            )

            stroke_path.M(first_vertex.x, first_vertex.y)
            for v in vertices[1:]:
                stroke_path.L(v.x, v.y)

            if vertices_are_closed:
                stroke_path.Z()

            group.append(stroke_path)

    def _render_with_holes(
        self,
        group,
        contours: VertexContours,
        has_fill,
        has_stroke,
        fill_color,
        fill_opacity,
        stroke_color,
        stroke_opacity,
        stroke_width,
        holes_stroke_color,
        holes_stroke_opacity,
        holes_stroke_width,
        state,
        drawing: Optional[dw.Drawing],
    ):
        """Render a shape with holes using SVG masks

        Strategy:
        1. Create a mask with white outer contour and black holes
        2. Add mask to drawing's defs section
        3. Apply mask to fill via mask attribute
        4. Render strokes separately
        """
        import random

        mask_id = f"hole-mask-{random.randint(1000000, 9999999)}"

        outer_verts = contours.outer.vertices

        # Create mask
        mask = dw.Mask(id=mask_id)

        # Mask: White outer contour (reveals)
        outer_mask_path = dw.Path(fill="white")
        if outer_verts:
            outer_mask_path.M(outer_verts[0].x, outer_verts[0].y)
            for v in outer_verts[1:]:
                outer_mask_path.L(v.x, v.y)
            outer_mask_path.Z()
        mask.append(outer_mask_path)

        # Mask: Black holes (hides)
        for hole in contours.holes:
            hole_mask_path = dw.Path(fill="black")
            hole_verts = hole.vertices
            if hole_verts:
                hole_mask_path.M(hole_verts[0].x, hole_verts[0].y)
                for v in hole_verts[1:]:
                    hole_mask_path.L(v.x, v.y)
                hole_mask_path.Z()
            mask.append(hole_mask_path)

        # Add mask to drawing's defs section (use append_def to avoid <use> element)
        if drawing is not None:
            drawing.append_def(mask)

        # Render fill with mask applied
        if has_fill:
            fill_path = dw.Path(
                fill=fill_color.to_rgb_string(),
                fill_opacity=fill_opacity,
                stroke="none",
                mask=f"url(#{mask_id})",
            )

            fill_path.M(outer_verts[0].x, outer_verts[0].y)
            for v in outer_verts[1:]:
                fill_path.L(v.x, v.y)
            fill_path.Z()

            group.append(fill_path)

        # Render strokes (not affected by mask)
        if has_stroke:
            kwargs = {}
            if hasattr(state, "stroke_linecap") and state.stroke_linecap is not None:
                kwargs["stroke_linecap"] = state.stroke_linecap

            # Outer stroke
            outer_stroke_path = dw.Path(
                fill="none",
                stroke=stroke_color.to_rgb_string(),
                stroke_opacity=stroke_opacity,
                stroke_width=stroke_width,
                **kwargs,
            )

            outer_stroke_path.M(outer_verts[0].x, outer_verts[0].y)
            for v in outer_verts[1:]:
                outer_stroke_path.L(v.x, v.y)
            outer_stroke_path.Z()

            group.append(outer_stroke_path)

            # Hole strokes (need mask applied to hide strokes in overlapping holes)
            # Double the stroke width because mask cuts through the middle of the stroke
            for hole in contours.holes:
                hole_verts = hole.vertices
                if hole_verts:
                    hole_stroke_path = dw.Path(
                        fill="none",
                        stroke=holes_stroke_color.to_rgb_string(),
                        stroke_opacity=holes_stroke_opacity,
                        stroke_width=holes_stroke_width
                        * 2,  # Double width - mask hides half
                        mask=f"url(#{mask_id})",  # Apply mask to hide overlapping hole strokes
                        **kwargs,
                    )

                    hole_stroke_path.M(hole_verts[0].x, hole_verts[0].y)
                    for v in hole_verts[1:]:
                        hole_stroke_path.L(v.x, v.y)
                    hole_stroke_path.Z()

                    group.append(hole_stroke_path)
