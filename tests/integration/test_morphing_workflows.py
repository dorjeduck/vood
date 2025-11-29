"""Integration tests for complete morphing workflows"""

import pytest
from pathlib import Path

from vood.component.state import (
    CircleState,
    RectangleState,
    TriangleState,
    StarState,
    PolygonState,
    RingState,
    PolyRingState,
)
from vood.core.color import Color
from vood.velement import VElement
from vood.vscene import VScene
from vood.transition.easing import in_out, linear


@pytest.mark.integration
class TestBasicMorphing:
    """Test basic shape-to-shape morphing"""

    def test_circle_to_rectangle_morph(self):
        """Test morphing circle to rectangle"""
        state1 = CircleState(radius=50, _num_vertices=64)
        state2 = RectangleState(width=100, height=60, _num_vertices=64)

        element = VElement(keystates=[state1, state2])

        # Should create valid morphing animation
        assert element is not None
        assert len(element.keystates) == 2

    def test_triangle_to_hexagon_morph(self):
        """Test morphing triangle to hexagon"""
        state1 = TriangleState(size=80, _num_vertices=60)
        state2 = PolygonState(size=50, num_sides=6, _num_vertices=60)

        element = VElement(keystates=[state1, state2])

        assert element is not None

    def test_star_to_circle_morph(self):
        """Test morphing star to circle"""
        state1 = StarState(
            outer_radius=80, inner_radius=40, num_points_star=5, _num_vertices=100
        )
        state2 = CircleState(radius=60, _num_vertices=100)

        element = VElement(keystates=[state1, state2])

        assert element is not None

    def test_multi_keystate_morph_sequence(self):
        """Test morphing through multiple keystates"""
        state1 = CircleState(radius=50, _num_vertices=64)
        state2 = TriangleState(size=80, _num_vertices=64)
        state3 = RectangleState(width=90, height=90, _num_vertices=64)
        state4 = CircleState(radius=60, _num_vertices=64)

        element = VElement(keystates=[state1, state2, state3, state4])

        assert len(element.keystates) == 4


@pytest.mark.integration
class TestHoleMorphing:
    """Test morphing with holes (perforated shapes)"""

    def test_circle_to_ring_morph(self):
        """Test morphing solid circle to ring (hole appears)"""
        state1 = CircleState(radius=80, _num_vertices=64)
        state2 = RingState(outer_radius=80, inner_radius=40, _num_vertices=64)

        element = VElement(keystates=[state1, state2])

        assert element is not None
        assert len(element.keystates) == 2

    def test_ring_to_circle_morph(self):
        """Test morphing ring to solid circle (hole disappears)"""
        state1 = RingState(outer_radius=80, inner_radius=40, _num_vertices=64)
        state2 = CircleState(radius=80, _num_vertices=64)

        element = VElement(keystates=[state1, state2])

        assert element is not None

    def test_ring_size_change_morph(self):
        """Test morphing between rings with different sizes"""
        state1 = RingState(outer_radius=100, inner_radius=50, _num_vertices=64)
        state2 = RingState(outer_radius=80, inner_radius=60, _num_vertices=64)

        element = VElement(keystates=[state1, state2])

        assert element is not None

    def test_polygon_ring_morph_sequence(self):
        """Test morphing sequence with perforated polygons"""
        state1 = PolyRingState(
            outer_size=100, inner_size=50, num_edges=6, _num_vertices=72
        )
        state2 = PolyRingState(
            outer_size=100, inner_size=50, num_edges=8, _num_vertices=72
        )

        element = VElement(keystates=[state1, state2])

        assert element is not None


@pytest.mark.integration
class TestColorTransitions:
    """Test color transitions during morphing"""

    def test_color_gradient_morph(self):
        """Test morphing with color gradient"""
        state1 = CircleState(radius=50, fill_color=Color("#FF0000"), _num_vertices=64)
        state2 = CircleState(radius=50, fill_color=Color("#0000FF"), _num_vertices=64)

        element = VElement(keystates=[state1, state2])

        assert element is not None

    def test_multi_color_transition(self):
        """Test morphing through multiple colors"""
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
        keystates = [
            CircleState(radius=50, fill_color=Color(c), _num_vertices=64) for c in colors
        ]

        element = VElement(keystates=keystates)

        assert len(element.keystates) == 4

    def test_opacity_transition(self):
        """Test morphing with opacity change"""
        state1 = CircleState(radius=50, fill_opacity=1.0, _num_vertices=64)
        state2 = CircleState(radius=50, fill_opacity=0.0, _num_vertices=64)

        element = VElement(keystates=[state1, state2])

        assert element is not None


@pytest.mark.integration
class TestTransformAnimations:
    """Test animations with transforms (position, rotation, scale)"""

    def test_position_and_morph_combined(self):
        """Test morphing combined with position change"""
        state1 = CircleState(x=-100, y=-100, radius=50, _num_vertices=64)
        state2 = RectangleState(x=100, y=100, width=80, height=60, _num_vertices=64)

        element = VElement(keystates=[state1, state2])

        assert element is not None

    def test_rotation_during_morph(self):
        """Test morphing with rotation"""
        state1 = RectangleState(width=100, height=60, rotation=0, _num_vertices=64)
        state2 = RectangleState(width=100, height=60, rotation=180, _num_vertices=64)

        element = VElement(keystates=[state1, state2])

        assert element is not None

    def test_scale_during_morph(self):
        """Test morphing with scale change"""
        state1 = CircleState(radius=50, scale=0.5, _num_vertices=64)
        state2 = StarState(
            outer_radius=80, inner_radius=40, num_points_star=5, scale=2.0, _num_vertices=64
        )

        element = VElement(keystates=[state1, state2])

        assert element is not None

    def test_complex_transform_sequence(self):
        """Test complex sequence with all transforms"""
        keystates = [
            CircleState(
                x=0, y=0, radius=50, scale=1.0, rotation=0, fill_opacity=1.0, _num_vertices=64
            ),
            CircleState(
                x=100,
                y=0,
                radius=50,
                scale=1.5,
                rotation=90,
                fill_opacity=0.7,
                _num_vertices=64,
            ),
            CircleState(
                x=100,
                y=100,
                radius=50,
                scale=0.8,
                rotation=180,
                fill_opacity=1.0,
                _num_vertices=64,
            ),
            CircleState(
                x=0,
                y=0,
                radius=50,
                scale=1.0,
                rotation=360,
                fill_opacity=1.0,
                _num_vertices=64,
            ),
        ]

        element = VElement(keystates=keystates)

        assert len(element.keystates) == 4


@pytest.mark.integration
class TestEasingIntegration:
    """Test easing functions in morphing"""

    def test_linear_easing_morph(self):
        """Test morphing with linear easing"""
        state1 = CircleState(radius=50, _num_vertices=64)
        state2 = RectangleState(width=80, height=60, _num_vertices=64)

        element = VElement(keystates=[state1, state2], property_easing={"radius": linear, "width": linear, "height": linear})

        assert element is not None

    def test_in_out_easing_morph(self):
        """Test morphing with in_out easing"""
        state1 = TriangleState(size=80, _num_vertices=60)
        state2 = PolygonState(size=50, num_sides=6, _num_vertices=60)

        element = VElement(keystates=[state1, state2], property_easing={"size": in_out})

        assert element is not None

    def test_in_out_easing_position_morph(self):
        """Test morphing position with in_out easing"""
        state1 = CircleState(x=0, radius=50, _num_vertices=64)
        state2 = CircleState(x=200, radius=50, _num_vertices=64)

        element = VElement(keystates=[state1, state2], property_easing={"x": in_out})

        assert element is not None

    def test_per_property_easing(self):
        """Test morphing with per-property easing"""
        state1 = CircleState(x=0, y=0, radius=50, _num_vertices=64)
        state2 = CircleState(x=200, y=200, radius=100, _num_vertices=64)

        element = VElement(
            keystates=[state1, state2],
            property_easing={"x": linear, "y": in_out, "radius": in_out},
        )

        assert element is not None


@pytest.mark.integration
class TestSceneIntegration:
    """Test complete scene rendering with morphing"""

    def test_single_element_in_scene(self):
        """Test rendering single morphing element in scene"""
        state1 = CircleState(radius=50, _num_vertices=64)
        state2 = RectangleState(width=100, height=60, _num_vertices=64)

        element = VElement(keystates=[state1, state2])
        scene = VScene(width=800, height=600)
        scene.add_element(element)

        # Should render without errors
        assert scene is not None
        assert len(scene.elements) == 1

    def test_multiple_elements_in_scene(self):
        """Test rendering multiple morphing elements"""
        element1 = VElement(
            keystates=[
                CircleState(x=-100, radius=50, _num_vertices=64),
                CircleState(x=-100, radius=75, _num_vertices=64),
            ]
        )

        element2 = VElement(
            keystates=[
                RectangleState(x=100, width=60, height=60, _num_vertices=64),
                RectangleState(x=100, width=90, height=90, _num_vertices=64),
            ]
        )

        scene = VScene(width=800, height=600)
        scene.add_element(element1)
        scene.add_element(element2)

        assert len(scene.elements) == 2

    def test_scene_with_varied_animations(self):
        """Test scene with multiple different animations"""
        # Morphing element
        morph_element = VElement(
            keystates=[
                CircleState(x=-200, radius=50, _num_vertices=64),
                StarState(
                    x=-200,
                    outer_radius=60,
                    inner_radius=30,
                    num_points_star=5,
                    _num_vertices=64,
                ),
            ]
        )

        # Color transition element
        color_element = VElement(
            keystates=[
                CircleState(
                    x=0, radius=40, fill_color=Color("#FF0000"), _num_vertices=64
                ),
                CircleState(
                    x=0, radius=40, fill_color=Color("#0000FF"), _num_vertices=64
                ),
            ]
        )

        # Position animation element
        move_element = VElement(
            keystates=[
                RectangleState(x=200, y=-100, width=50, height=50, _num_vertices=64),
                RectangleState(x=200, y=100, width=50, height=50, _num_vertices=64),
            ]
        )

        scene = VScene(width=800, height=600)
        scene.add_element(morph_element)
        scene.add_element(color_element)
        scene.add_element(move_element)

        assert len(scene.elements) == 3

    def test_scene_frame_generation(self):
        """Test generating frames from scene"""
        state1 = CircleState(radius=50, _num_vertices=64)
        state2 = RectangleState(width=80, height=60, _num_vertices=64)

        element = VElement(keystates=[state1, state2])
        scene = VScene(width=400, height=300)
        scene.add_element(element)

        # Generate a frame at different times
        frame_start = scene.to_drawing(frame_time=0.0)
        frame_mid = scene.to_drawing(frame_time=0.5)
        frame_end = scene.to_drawing(frame_time=1.0)

        assert frame_start is not None
        assert frame_mid is not None
        assert frame_end is not None


@pytest.mark.integration
class TestPropertyKeystates:
    """Test property-level keystates override"""

    def test_property_keystate_override(self):
        """Test overriding specific property with property keystates"""
        state1 = CircleState(x=0, y=0, radius=50, _num_vertices=64)
        state2 = CircleState(x=100, y=100, radius=100, _num_vertices=64)

        # Override x property with custom keystate
        element = VElement(
            keystates=[state1, state2],
            property_keystates={"x": [(0, 0.0), (50, 0.5), (100, 1.0)]},
        )

        assert element is not None

    def test_multiple_property_keystates(self):
        """Test overriding multiple properties"""
        state1 = CircleState(
            x=0, y=0, radius=50, fill_color=Color("#FF0000"), _num_vertices=64
        )
        state2 = CircleState(
            x=200, y=200, radius=100, fill_color=Color("#0000FF"), _num_vertices=64
        )

        element = VElement(
            keystates=[state1, state2],
            property_keystates={
                "x": [(0, 0.0), (100, 0.5), (200, 1.0)],
                "radius": [(50, 0.0), (150, 0.3), (100, 1.0)],
            },
        )

        assert element is not None


@pytest.mark.integration
class TestComplexMorphingScenarios:
    """Test complex real-world morphing scenarios"""

    def test_loading_spinner_animation(self):
        """Test creating a loading spinner animation"""
        keystates = [
            CircleState(radius=50, rotation=angle, _num_vertices=64)
            for angle in range(0, 361, 45)
        ]

        element = VElement(keystates=keystates)

        assert len(element.keystates) == 9

    def test_breathing_effect(self):
        """Test creating breathing/pulsing effect"""
        keystates = [
            CircleState(radius=50, fill_opacity=1.0, scale=1.0, _num_vertices=64),
            CircleState(radius=50, fill_opacity=0.5, scale=1.2, _num_vertices=64),
            CircleState(radius=50, fill_opacity=1.0, scale=1.0, _num_vertices=64),
        ]

        element = VElement(keystates=keystates)

        assert len(element.keystates) == 3

    def test_shape_cycle_animation(self):
        """Test cycling through multiple shapes"""
        keystates = [
            CircleState(radius=50, _num_vertices=64),
            TriangleState(size=80, _num_vertices=64),
            RectangleState(width=70, height=70, _num_vertices=64),
            PolygonState(size=50, num_sides=6, _num_vertices=64),
            CircleState(radius=50, _num_vertices=64),  # Back to start
        ]

        element = VElement(keystates=keystates)

        assert len(element.keystates) == 5

    def test_tunnel_effect_with_rings(self):
        """Test tunnel effect using rings"""
        keystates = [
            RingState(
                outer_radius=20 + i * 20,
                inner_radius=10 + i * 10,
                fill_opacity=1.0 - i * 0.15,
                _num_vertices=64,
            )
            for i in range(5)
        ]

        # Create multiple ring elements at different z-depths (scales)
        elements = [VElement(keystates=[state]) for state in keystates]

        assert len(elements) == 5
