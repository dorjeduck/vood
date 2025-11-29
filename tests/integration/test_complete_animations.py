"""Integration tests for complete animation workflows"""

import pytest
from pathlib import Path
from vood.velement import VElement
from vood.vscene import VScene
from vood.component.state.circle import CircleState
from vood.component.state.rectangle import RectangleState
from vood.component.state.text import TextState
from vood.transition.easing import linear, in_out
from vood.core.color import Color
from vood.animation.atomic.fade import fade
from vood.animation.atomic.slide import slide
from vood.animation.atomic.scale import scale


@pytest.mark.integration
class TestBasicAnimations:
    """Test basic animation workflows"""

    def test_simple_position_animation(self):
        """Test animating a circle's position"""
        state1 = CircleState(x=0, y=0, radius=50)
        state2 = CircleState(x=100, y=100, radius=50)

        element = VElement(keystates=[state1, state2])

        # Get frame at t=0.5
        frame_state = element.get_frame(0.5)

        # Position should be interpolated
        assert frame_state.x == 50
        assert frame_state.y == 50
        assert frame_state.radius == 50

    def test_color_fade_animation(self):
        """Test fading color animation"""
        state1 = CircleState(
            x=0, y=0, radius=50,
            fill_color=Color("#FF0000")
        )
        state2 = CircleState(
            x=0, y=0, radius=50,
            fill_color=Color("#0000FF")
        )

        element = VElement(keystates=[state1, state2])
        frame_state = element.get_frame(0.5)

        # Color should be interpolated (purplish)
        assert frame_state.fill_color.r > 0
        assert frame_state.fill_color.b > 0

    def test_multi_keystate_animation(self):
        """Test animation with multiple keystates"""
        states = [
            CircleState(x=0, y=0, radius=50),
            CircleState(x=50, y=50, radius=75),
            CircleState(x=100, y=100, radius=100),
        ]

        element = VElement(keystates=states)

        # Test various points
        frame_0 = element.get_frame(0.0)
        frame_25 = element.get_frame(0.25)
        frame_50 = element.get_frame(0.5)
        frame_75 = element.get_frame(0.75)
        frame_100 = element.get_frame(1.0)

        assert frame_0.x == 0
        assert frame_50.x == 50
        assert frame_100.x == 100

    def test_opacity_animation(self):
        """Test opacity fade animation"""
        state1 = CircleState(x=0, y=0, radius=50, opacity=0.0)
        state2 = CircleState(x=0, y=0, radius=50, opacity=1.0)

        element = VElement(keystates=[state1, state2])
        frame_state = element.get_frame(0.5)

        assert frame_state.opacity == 0.5


@pytest.mark.integration
class TestSceneComposition:
    """Test scene composition and rendering"""

    def test_scene_with_single_element(self):
        """Test scene containing single element"""
        state = CircleState(x=0, y=0, radius=50)
        element = VElement(state=state)

        scene = VScene(width=800, height=600)
        scene.add_element(element)

        # Should render without error
        drawing = scene.to_drawing(frame_time=0.0)
        assert drawing is not None

    def test_scene_with_multiple_elements(self):
        """Test scene with multiple elements"""
        circle = VElement(state=CircleState(x=-100, y=0, radius=50))
        rect = VElement(state=RectangleState(x=100, y=0, width=100, height=60))

        scene = VScene(width=800, height=600)
        scene.add_element(circle)
        scene.add_element(rect)

        drawing = scene.to_drawing(frame_time=0.0)
        assert drawing is not None

    def test_scene_with_animated_elements(self):
        """Test scene with animated elements"""
        states1 = [
            CircleState(x=-100, y=0, radius=50),
            CircleState(x=100, y=0, radius=50),
        ]
        states2 = [
            RectangleState(x=100, y=0, width=50, height=50),
            RectangleState(x=-100, y=0, width=50, height=50),
        ]

        element1 = VElement(keystates=states1)
        element2 = VElement(keystates=states2)

        scene = VScene(width=800, height=600)
        scene.add_element(element1)
        scene.add_element(element2)

        # Render at different times
        drawing_0 = scene.to_drawing(frame_time=0.0)
        drawing_50 = scene.to_drawing(frame_time=0.5)
        drawing_100 = scene.to_drawing(frame_time=1.0)

        assert drawing_0 is not None
        assert drawing_50 is not None
        assert drawing_100 is not None


@pytest.mark.integration
class TestAnimationHelpers:
    """Test animation helper functions"""

@pytest.mark.integration
class TestPropertyKeystates:
    """Test property-level keystate overrides"""

    def test_property_keystate_override(self):
        """Test property keystate overriding element keystates"""
        states = [
            CircleState(x=0, y=0, radius=50, fill_color=Color("#FF0000")),
            CircleState(x=100, y=100, radius=50, fill_color=Color("#FF0000")),
        ]

        # Override fill color to change independently
        property_keystates = {
            "fill_color": [
                (0.0, Color("#FF0000")),
                (1.0, Color("#0000FF")),
            ]
        }

        element = VElement(keystates=states, property_keystates=property_keystates)

        # Color should interpolate according to property keystates
        frame_50 = element.get_frame(0.5)
        assert frame_50.fill_color.r > 0
        assert frame_50.fill_color.b > 0


@pytest.mark.integration
@pytest.mark.slow
class TestComplexAnimations:
    """Test complex animation scenarios"""

    def test_morphing_shapes(self):
        """Test morphing between different vertex-based shapes"""
        # This would require vertex-based states like PolygonState
        # Testing basic state changes for now
        states = [
            CircleState(x=0, y=0, radius=50),
            CircleState(x=0, y=0, radius=100),
            CircleState(x=0, y=0, radius=50),
        ]

        element = VElement(keystates=states)

        # Should smoothly interpolate radius
        frame_25 = element.get_frame(0.25)
        frame_75 = element.get_frame(0.75)

        assert frame_25.radius > 50
        assert frame_25.radius < 100
        assert frame_75.radius > 50
        assert frame_75.radius < 100

    def test_rotation_animation(self):
        """Test rotation with angle wraparound"""
        states = [
            RectangleState(x=0, y=0, width=100, height=50, rotation=350),
            RectangleState(x=0, y=0, width=100, height=50, rotation=10),
        ]

        element = VElement(keystates=states)

        # Should take shortest path through 0/360
        frame_50 = element.get_frame(0.5)
        # Rotation should be near 0 or 360
        assert frame_50.rotation < 10 or frame_50.rotation > 350

    def test_combined_transformations(self):
        """Test combining multiple transformations"""
        states = [
            CircleState(x=0, y=0, radius=50, scale=0.5, opacity=0.0, rotation=0),
            CircleState(x=100, y=100, radius=75, scale=1.5, opacity=1.0, rotation=180),
        ]

        element = VElement(keystates=states)
        frame_50 = element.get_frame(0.5)

        # All properties should interpolate
        assert frame_50.x == 50
        assert frame_50.y == 50
        assert frame_50.radius == 62.5
        assert frame_50.scale == 1.0
        assert frame_50.opacity == 0.5
        assert frame_50.rotation == 90


@pytest.mark.integration
class TestSceneExport:
    """Test scene export functionality"""


    def test_easing_override(self):
        """Test per-property easing override"""
        from vood.velement.keystate import KeyState

        state1 = CircleState(x=0, y=0, radius=50)
        state2 = CircleState(x=100, y=0, radius=50)

        keystates = [
            KeyState(state=state1, time=0.0),
            KeyState(state=state2, time=1.0, easing={"x": in_out}),
        ]

        element = VElement(keystates=keystates)

        # With in_out easing, movement should be slower at start/end
        frame_25 = element.get_frame(0.25)
        frame_50 = element.get_frame(0.5)

        # At 0.25, should have moved less than 25 due to ease-in
        assert frame_25.x < 25
        # At 0.5, should be at 50 (midpoint)
        assert abs(frame_50.x - 50) < 5


@pytest.mark.integration
class TestEdgeCases:
    """Test edge cases in complete workflows"""


    def test_very_short_animation_segment(self):
        """Test animation with very short time segment"""
        states = [
            (0.499, CircleState(x=0, y=0, radius=50)),
            (0.501, CircleState(x=100, y=100, radius=50)),
        ]

        element = VElement(keystates=states)

        # Should handle very short segment
        frame = element.get_frame(0.5)
        assert frame is not None

    def test_many_keystates(self):
        """Test animation with many keystates"""
        states = [
            CircleState(x=i*10, y=i*10, radius=50)
            for i in range(20)
        ]

        element = VElement(keystates=states)

        # Should handle many keystates
        frame_50 = element.get_frame(0.5)
        assert frame_50 is not None
        # Should be roughly in the middle position
        assert 80 < frame_50.x < 120
