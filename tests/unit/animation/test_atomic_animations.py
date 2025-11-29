"""Tests for atomic animation helpers"""

import pytest

from vood.component.state import CircleState, RectangleState, TextState
from vood.core.color import Color
from vood.animation.atomic import (
    fade, scale, rotate, slide, pop, step, trim
)
from vood.velement.keystate import KeyState


@pytest.mark.unit
class TestFadeAnimation:
    """Test fade animation helper"""

    def test_fade_in_basic(self):
        """Test basic fade in animation - fade from transparent to opaque"""
        state1 = CircleState(radius=50, opacity=0.0)
        state2 = CircleState(radius=50, opacity=1.0)
        keystates = fade(state1, state2, duration=0.2)

        assert isinstance(keystates, list)
        assert len(keystates) >= 2
        assert all(isinstance(ks, KeyState) for ks in keystates)

        # Should have keystates with varying opacity levels
        opacities = [ks.state.opacity for ks in keystates]
        # Should have at least one keystate that is transparent
        assert 0.0 in opacities or min(opacities) < 1.0

    def test_fade_out_basic(self):
        """Test basic fade out animation - fade from opaque to transparent"""
        state1 = CircleState(radius=50, opacity=1.0)
        state2 = CircleState(radius=50, opacity=0.0)
        keystates = fade(state1, state2, duration=0.2)

        assert isinstance(keystates, list)
        assert len(keystates) >= 2

        # Should have keystates with varying opacity
        opacities = [ks.state.opacity for ks in keystates]
        # Should have at least one keystate that is transparent
        assert 0.0 in opacities or min(opacities) < 1.0

    def test_fade_with_at_time(self):
        """Test fade with custom timing"""
        state1 = CircleState(radius=50)
        state2 = CircleState(radius=50, fill_color=Color("#FF0000"))
        keystates = fade(state1, state2, at_time=0.5, duration=0.2)

        assert isinstance(keystates, list)
        assert len(keystates) >= 2

    def test_fade_preserves_other_properties(self):
        """Test that fade preserves non-opacity properties"""
        state1 = CircleState(
            x=100, y=100,
            radius=50,
            fill_color=Color("#FF0000"),
            rotation=45
        )
        state2 = CircleState(
            x=100, y=100,
            radius=50,
            fill_color=Color("#00FF00"),
            rotation=45
        )
        keystates = fade(state1, state2, duration=0.2)

        # All keystates should preserve x, y, radius, rotation
        for ks in keystates:
            assert ks.state.x == 100
            assert ks.state.y == 100
            assert ks.state.radius == 50
            assert ks.state.rotation == 45


@pytest.mark.unit
class TestScaleAnimation:
    """Test scale animation helper"""

    def test_scale_up_basic(self):
        """Test basic scale up animation"""
        state1 = CircleState(radius=50, scale=0.0)
        state2 = CircleState(radius=50, scale=1.0)
        keystates = scale(state1, state2, duration=0.3)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)

        # Should have keystates with varying scales
        scales = [ks.state.scale for ks in keystates]
        # Should have at least one keystate at minimum scale
        assert 0.0 in scales or min(scales) < 1.0

    def test_scale_down_basic(self):
        """Test basic scale down animation"""
        state1 = CircleState(radius=50, scale=1.0)
        state2 = CircleState(radius=50, scale=0.0)
        keystates = scale(state1, state2, duration=0.3)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)

        # Should have keystates with varying scales
        scales = [ks.state.scale for ks in keystates]
        # Should have at least one keystate at minimum scale
        assert 0.0 in scales or min(scales) < 1.0

    def test_scale_with_custom_min(self):
        """Test scale with custom minimum scale"""
        state1 = CircleState(radius=50)
        state2 = CircleState(radius=75)
        keystates = scale(
            state1, state2,
            min_scale=0.5,
            duration=0.3
        )

        assert isinstance(keystates, list)
        assert len(keystates) >= 2


@pytest.mark.unit
class TestRotateAnimation:
    """Test rotate animation helper"""

    def test_rotate_clockwise_basic(self):
        """Test basic clockwise rotation"""
        state1 = RectangleState(width=100, height=60, rotation=0)
        state2 = RectangleState(width=100, height=60, rotation=360)
        keystates = rotate(state1, state2, angle=360, duration=0.3)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)

    def test_rotate_counterclockwise_basic(self):
        """Test basic counterclockwise rotation"""
        state1 = RectangleState(width=100, height=60, rotation=360)
        state2 = RectangleState(width=100, height=60, rotation=0)
        keystates = rotate(state1, state2, angle=360, duration=0.3)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)

    def test_rotate_full_rotation(self):
        """Test rotation with full 360 degree rotation"""
        state1 = RectangleState(width=100, height=60)
        state2 = RectangleState(width=100, height=60)
        keystates = rotate(state1, state2, angle=720, duration=0.5)

        assert isinstance(keystates, list)
        assert len(keystates) >= 2


@pytest.mark.unit
class TestSlideAnimation:
    """Test slide animation helper"""

    def test_slide_left_basic(self):
        """Test basic slide left animation"""
        state1 = CircleState(x=100, y=0, radius=50)
        state2 = CircleState(x=0, y=0, radius=50)
        keystates = slide(state1, state2, direction="left", distance=100, duration=0.3)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)

        # X should vary during slide
        x_values = [ks.state.x for ks in keystates]
        assert len(set(x_values)) > 1  # At least 2 different x values

    def test_slide_right_basic(self):
        """Test basic slide right animation"""
        state1 = CircleState(x=0, y=0, radius=50)
        state2 = CircleState(x=100, y=0, radius=50)
        keystates = slide(state1, state2, direction="right", distance=100, duration=0.3)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)

        # X should vary during slide
        x_values = [ks.state.x for ks in keystates]
        assert len(set(x_values)) > 1

    def test_slide_up_basic(self):
        """Test basic slide up animation"""
        state1 = CircleState(x=0, y=0, radius=50)
        state2 = CircleState(x=0, y=100, radius=50)
        keystates = slide(state1, state2, direction="up", distance=100, duration=0.3)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)

        # Y should vary during animation
        y_values = [ks.state.y for ks in keystates]
        assert len(set(y_values)) > 1

    def test_slide_down_basic(self):
        """Test basic slide down animation"""
        state1 = CircleState(x=0, y=100, radius=50)
        state2 = CircleState(x=0, y=50, radius=50)
        keystates = slide(state1, state2, direction="down", distance=50, duration=0.3)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)


@pytest.mark.unit
class TestPopAnimation:
    """Test pop animation helper"""

    def test_pop_basic(self):
        """Test basic pop animation"""
        state1 = CircleState(radius=50)
        state2 = CircleState(radius=50)
        keystates = pop(state1, state2, duration=0.2)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)
        assert len(keystates) >= 2

    def test_pop_switches_states(self):
        """Test pop with state change"""
        state1 = CircleState(radius=50, fill_color=Color("#FF0000"))
        state2 = CircleState(radius=75, fill_color=Color("#0000FF"))
        keystates = pop(state1, state2, duration=0.2)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)


@pytest.mark.unit
class TestStepAnimation:
    """Test step animation helper"""

    def test_step_basic(self):
        """Test basic step animation (instant change)"""
        state1 = CircleState(x=0, y=0, radius=50, fill_color=Color("#FF0000"))
        state2 = CircleState(x=100, y=100, radius=75, fill_color=Color("#0000FF"))

        keystates = step(state1, state2, at_time=0.5)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)
        assert len(keystates) >= 2

    def test_step_at_midpoint(self):
        """Test step animation with custom timing"""
        state1 = CircleState(radius=50)
        state2 = CircleState(radius=100)

        keystates = step(state1, state2, at_time=0.5)

        assert isinstance(keystates, list)
        assert len(keystates) >= 2


@pytest.mark.unit
class TestTrimAnimation:
    """Test trim animation helper"""

    def test_trim_basic(self):
        """Test basic trim animation"""
        state1 = CircleState(x=0, y=0, radius=50)
        state2 = CircleState(x=100, y=100, radius=50)
        keystates = trim(state1, state2, duration=0.2)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)
        assert len(keystates) >= 2

    def test_trim_with_timing(self):
        """Test trim animation with custom timing"""
        state1 = CircleState(x=0, y=0, radius=50)
        state2 = CircleState(x=100, y=100, radius=50)
        keystates = trim(state1, state2, at_time=0.75, duration=0.2)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)


@pytest.mark.unit
class TestAnimationComposition:
    """Test composing multiple animations"""

    def test_sequential_animations(self):
        """Test creating sequential animations"""
        from vood.animation.atomic import sequential_transition

        state1 = CircleState(x=0, y=0, radius=50)
        state2 = CircleState(x=100, y=0, radius=50)
        state3 = CircleState(x=100, y=100, radius=50)

        keystates = sequential_transition(
            states=[state1, state2, state3],
            transition_func=fade,
            transition_factor=0.5
        )

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)
        assert len(keystates) >= 3


@pytest.mark.unit
class TestAnimationPreservation:
    """Test that animations preserve properties correctly"""

    def test_fade_preserves_position(self):
        """Test that fade animation preserves position"""
        state1 = CircleState(x=123, y=456, radius=50)
        state2 = CircleState(x=123, y=456, radius=50)
        keystates = fade(state1, state2, duration=0.2)

        for ks in keystates:
            assert ks.state.x == 123
            assert ks.state.y == 456

    def test_slide_preserves_scale(self):
        """Test that slide animation preserves scale"""
        state1 = CircleState(x=0, y=0, radius=50, scale=2.0)
        state2 = CircleState(x=100, y=0, radius=50, scale=2.0)
        keystates = slide(state1, state2, direction="right", distance=100, duration=0.3)

        for ks in keystates:
            assert ks.state.scale == 2.0

    def test_rotate_preserves_color(self):
        """Test that rotate animation preserves color"""
        state1 = RectangleState(
            width=100, height=60,
            fill_color=Color("#FF0000")
        )
        state2 = RectangleState(
            width=100, height=60,
            fill_color=Color("#FF0000")
        )
        keystates = rotate(state1, state2, angle=180, duration=0.3)

        for ks in keystates:
            assert ks.state.fill_color == Color("#FF0000")


@pytest.mark.unit
class TestAnimationEdgeCases:
    """Test edge cases in animation helpers"""

    def test_zero_duration_animation(self):
        """Test animation with zero duration"""
        state1 = CircleState(radius=50)
        state2 = CircleState(radius=50)
        keystates = fade(state1, state2, duration=0.0)
        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)

    def test_very_small_duration(self):
        """Test animation with very small duration"""
        state1 = CircleState(radius=50)
        state2 = CircleState(radius=50)
        keystates = fade(state1, state2, duration=0.001)
        # Should handle gracefully
        assert isinstance(keystates, list)

    def test_animation_with_none_state_properties(self):
        """Test animations with Color.NONE"""
        state1 = CircleState(
            radius=50,
            fill_color=Color.NONE,
            stroke_color=Color.NONE
        )
        state2 = CircleState(
            radius=50,
            fill_color=Color.NONE,
            stroke_color=Color.NONE
        )
        keystates = scale(state1, state2, duration=0.3)

        assert isinstance(keystates, list)
        assert all(isinstance(ks, KeyState) for ks in keystates)
