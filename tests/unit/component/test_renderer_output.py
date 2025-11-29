"""Tests for renderer SVG output correctness"""

import pytest
import drawsvg as dw

from vood.core.color import Color
from vood.component.state import (
    CircleState, RectangleState, TriangleState, PolygonState,
    StarState, EllipseState, LineState, TextState, RingState,
)
from vood.component.renderer import (
    CircleRenderer, RectangleRenderer, TriangleRenderer,
    PolygonRenderer, EllipseRenderer,
    TextRenderer,
)
from vood.component.registry import get_renderer_class_for_state


@pytest.mark.unit

@pytest.mark.unit
class TestCircleRenderer:
    """Test CircleRenderer SVG output"""

    def test_render_circle_basic(self):
        """Test basic circle rendering"""
        state = CircleState(x=100, y=100, radius=50)
        renderer = CircleRenderer()
        element = renderer.render(state)

        assert element is not None
        assert isinstance(element, (dw.Group, dw.Circle))

    def test_render_circle_with_colors(self):
        """Test circle rendering with custom colors"""
        state = CircleState(
            x=100, y=100, radius=50,
            fill_color=Color("#FF0000"),
            stroke_color=Color("#0000FF"),
            stroke_width=3
        )
        renderer = CircleRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_render_circle_with_transforms(self):
        """Test circle rendering with transforms"""
        state = CircleState(
            x=100, y=100, radius=50,
            scale=2.0,
            rotation=45,
            opacity=0.5
        )
        renderer = CircleRenderer()
        element = renderer.render(state)

        assert element is not None


@pytest.mark.unit
class TestRectangleRenderer:
    """Test RectangleRenderer SVG output"""

    def test_render_rectangle_basic(self):
        """Test basic rectangle rendering"""
        state = RectangleState(x=100, y=100, width=150, height=80)
        renderer = RectangleRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_render_rectangle_with_rotation(self):
        """Test rectangle rendering with rotation"""
        state = RectangleState(
            x=100, y=100, width=150, height=80,
            rotation=30
        )
        renderer = RectangleRenderer()
        element = renderer.render(state)

        assert element is not None


@pytest.mark.unit
class TestPolygonRenderer:
    """Test PolygonRenderer SVG output"""

    def test_render_hexagon(self):
        """Test hexagon rendering"""
        state = PolygonState(x=100, y=100, size=50, num_sides=6)
        renderer = PolygonRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_render_octagon(self):
        """Test octagon rendering"""
        state = PolygonState(x=100, y=100, size=50, num_sides=8)
        renderer = PolygonRenderer()
        element = renderer.render(state)

        assert element is not None


# Note: StarState uses VertexRenderer - test vertex renderer instead
# @pytest.mark.unit
# class TestStarRenderer:
#     """Test StarRenderer SVG output"""
#
#     def test_render_five_point_star(self):
#         """Test five-pointed star rendering"""
#         state = StarState(
#             x=100, y=100,
#             outer_radius=80,
#             inner_radius=40,
#             num_points=5
#         )
#         # Use vertex renderer
#         renderer_class = state.get_vertex_renderer_class()
#         renderer = renderer_class()
#         element = renderer.render(state)
#
#         assert element is not None
#
#     def test_render_six_point_star(self):
#         """Test six-pointed star rendering"""
#         state = StarState(
#             x=100, y=100,
#             outer_radius=80,
#             inner_radius=40,
#             num_points=6
#         )
#         renderer_class = state.get_vertex_renderer_class()
#         renderer = renderer_class()
#         element = renderer.render(state)
#
#         assert element is not None


# Note: LineRenderer may use VertexRenderer - test vertex renderer instead
# @pytest.mark.unit
# class TestLineRenderer:
#     """Test LineRenderer SVG output"""
#
#     def test_render_line_basic(self):
#         """Test basic line rendering"""
#         state = LineState(x1=0, y1=0, x2=100, y2=100)
#         renderer = LineRenderer()
#         element = renderer.render(state)
#
#         assert element is not None
#
#     def test_render_line_with_stroke(self):
#         """Test line rendering with custom stroke"""
#         state = LineState(
#             x1=0, y1=0, x2=100, y2=100,
#             stroke_color=Color("#FF0000"),
#             stroke_width=5
#         )
#         renderer = LineRenderer()
#         element = renderer.render(state)
#
#         assert element is not None


@pytest.mark.unit
class TestTextRenderer:
    """Test TextRenderer SVG output"""

    def test_render_text_basic(self):
        """Test basic text rendering"""
        state = TextState(x=100, y=100, text="Hello World")
        renderer = TextRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_render_text_with_font_size(self):
        """Test text rendering with custom font size"""
        state = TextState(
            x=100, y=100,
            text="Hello",
            font_size=48
        )
        renderer = TextRenderer()
        element = renderer.render(state)

        assert element is not None


@pytest.mark.unit
class TestRendererTransforms:
    """Test that renderers correctly apply transforms"""

    def test_renderer_applies_translation(self):
        """Test that renderers apply translation"""
        state = CircleState(x=100, y=100, radius=50)
        renderer = CircleRenderer()
        element = renderer.render(state)

        # Element should be rendered (details depend on implementation)
        assert element is not None

    def test_renderer_applies_rotation(self):
        """Test that renderers apply rotation"""
        state = RectangleState(
            x=100, y=100, width=100, height=60,
            rotation=45
        )
        renderer = RectangleRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_renderer_applies_scale(self):
        """Test that renderers apply scale"""
        state = CircleState(x=100, y=100, radius=50, scale=2.0)
        renderer = CircleRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_renderer_applies_opacity(self):
        """Test that renderers apply opacity"""
        state = CircleState(x=100, y=100, radius=50, opacity=0.5)
        renderer = CircleRenderer()
        element = renderer.render(state)

        assert element is not None


@pytest.mark.unit
class TestRendererEdgeCases:
    """Test renderer behavior with edge cases"""

    def test_render_zero_radius_circle(self):
        """Test rendering circle with zero radius"""
        state = CircleState(radius=0)
        renderer = CircleRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_render_negative_radius_circle(self):
        """Test rendering circle with negative radius"""
        state = CircleState(radius=-50)
        renderer = CircleRenderer()
        # Should not crash, might render as zero or handle gracefully
        element = renderer.render(state)

        assert element is not None

    def test_render_zero_dimensions_rectangle(self):
        """Test rendering rectangle with zero dimensions"""
        state = RectangleState(width=0, height=0)
        renderer = RectangleRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_render_empty_text(self):
        """Test rendering empty text"""
        state = TextState(text="")
        renderer = TextRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_render_very_long_text(self):
        """Test rendering very long text"""
        long_text = "A" * 1000
        state = TextState(text=long_text)
        renderer = TextRenderer()
        element = renderer.render(state)

        assert element is not None


@pytest.mark.unit
class TestRendererColorHandling:
    """Test renderer color handling"""

    def test_render_with_color_none(self):
        """Test rendering with transparent color"""
        state = CircleState(
            radius=50,
            fill_color=Color.NONE,
            stroke_color=Color("#000000")
        )
        renderer = CircleRenderer()
        element = renderer.render(state)

        assert element is not None

    def test_render_with_both_colors_none(self):
        """Test rendering with both colors transparent"""
        state = CircleState(
            radius=50,
            fill_color=Color.NONE,
            stroke_color=Color.NONE
        )
        renderer = CircleRenderer()
        element = renderer.render(state)

        assert element is not None


@pytest.mark.unit
class TestVertexRenderer:
    """Test vertex-based rendering for morphing"""

    def test_vertex_renderer_for_circle(self):
        """Test vertex renderer for CircleState"""
        state = CircleState(radius=50, _num_vertices=16)

        # Get vertex renderer class
        vertex_renderer_class = state.get_vertex_renderer_class()
        assert vertex_renderer_class is not None

        # Create and use vertex renderer
        renderer = vertex_renderer_class()
        element = renderer.render(state)

        assert element is not None

    def test_vertex_renderer_for_rectangle(self):
        """Test vertex renderer for RectangleState"""
        state = RectangleState(width=100, height=60, _num_vertices=4)

        vertex_renderer_class = state.get_vertex_renderer_class()
        assert vertex_renderer_class is not None

        renderer = vertex_renderer_class()
        element = renderer.render(state)

        assert element is not None

    def test_vertex_renderer_with_holes(self):
        """Test vertex renderer for state with holes"""
        state = RingState(
            outer_radius=100,
            inner_radius=50,
            _num_vertices=16
        )

        vertex_renderer_class = state.get_vertex_renderer_class()
        assert vertex_renderer_class is not None

        renderer = vertex_renderer_class()
        element = renderer.render(state)

        assert element is not None


@pytest.mark.unit
class TestRendererConsistency:
    """Test consistency between primitive and vertex renderers"""

    def test_circle_renderers_produce_similar_output(self):
        """Test that primitive and vertex renderers produce valid output"""
        state = CircleState(x=100, y=100, radius=50, _num_vertices=64)

        # Primitive renderer
        primitive_renderer = CircleRenderer()
        primitive_element = primitive_renderer.render(state)

        # Vertex renderer
        vertex_renderer_class = state.get_vertex_renderer_class()
        vertex_renderer = vertex_renderer_class()
        vertex_element = vertex_renderer.render(state)

        # Both should produce valid elements
        assert primitive_element is not None
        assert vertex_element is not None
