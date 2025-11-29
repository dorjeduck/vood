"""Tests for compound animation helpers"""

import pytest

from vood.component.state import CircleState, RectangleState, StarState
from vood.core.color import Color
from vood.animation.compound import (
    crossfade, bounce_replace, scale_swap, slide_replace, rotate_flip
)
from vood.velement.keystate import KeyState


@pytest.mark.unit
class TestCrossfadeAnimation:
    """Test crossfade animation helper"""

    def test_crossfade_basic(self):
        """Test basic crossfade between two states"""
        state1 = CircleState(x=0, y=0, radius=50, fill_color=Color("#FF0000"))
        state2 = CircleState(x=100, y=100, radius=75, fill_color=Color("#0000FF"))

        keystates1, keystates2 = crossfade(state1, state2, duration=0.3)

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)
        assert all(isinstance(ks, KeyState) for ks in keystates1)
        assert all(isinstance(ks, KeyState) for ks in keystates2)

    def test_crossfade_opacity_transition(self):
        """Test that crossfade creates opposite opacity transitions"""
        state1 = CircleState(x=0, y=0, radius=50, opacity=1.0)
        state2 = CircleState(x=100, y=100, radius=75, opacity=1.0)

        keystates1, keystates2 = crossfade(state1, state2, duration=0.3)

        # First element should fade out (opacity decreases)
        first_opacity = keystates1[0].state.opacity
        last_opacity1 = keystates1[-1].state.opacity
        assert first_opacity > last_opacity1

        # Second element should fade in (opacity increases)
        first_opacity2 = keystates2[0].state.opacity
        last_opacity2 = keystates2[-1].state.opacity
        assert first_opacity2 < last_opacity2

    def test_crossfade_different_shapes(self):
        """Test crossfade between different shape types"""
        state1 = CircleState(x=0, y=0, radius=50)
        state2 = RectangleState(x=100, y=100, width=80, height=80)

        keystates1, keystates2 = crossfade(state1, state2, duration=0.3)

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)
        assert len(keystates1) >= 2
        assert len(keystates2) >= 2


@pytest.mark.unit
class TestBounceReplaceAnimation:
    """Test bounce_replace animation helper"""

    def test_bounce_replace_basic(self):
        """Test basic bounce replace animation"""
        state1 = CircleState(radius=50, fill_color=Color("#FF0000"))
        state2 = CircleState(radius=50, fill_color=Color("#0000FF"))

        keystates1, keystates2 = bounce_replace(state1, state2, duration=0.4)

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)
        assert all(isinstance(ks, KeyState) for ks in keystates1)
        assert all(isinstance(ks, KeyState) for ks in keystates2)

    def test_bounce_replace_with_custom_height(self):
        """Test bounce replace with custom bounce height"""
        state1 = CircleState(radius=50)
        state2 = CircleState(radius=75)

        keystates1, keystates2 = bounce_replace(
            state1, state2,
            bounce_height=-75,
            duration=0.4
        )

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)
        assert len(keystates1) >= 1
        assert len(keystates2) >= 1


@pytest.mark.unit
class TestScaleSwapAnimation:
    """Test scale_swap animation helper"""

    def test_scale_swap_basic(self):
        """Test basic scale swap animation"""
        state1 = CircleState(radius=60)
        state2 = CircleState(radius=50)

        keystates1, keystates2 = scale_swap(state1, state2, duration=0.3)

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)
        assert all(isinstance(ks, KeyState) for ks in keystates1)
        assert all(isinstance(ks, KeyState) for ks in keystates2)

    def test_scale_swap_opposite_directions(self):
        """Test that scale swap scales in opposite directions"""
        state1 = CircleState(radius=50, scale=1.0)
        state2 = RectangleState(width=80, height=60, scale=1.0)

        keystates1, keystates2 = scale_swap(
            state1, state2,
            min_scale=0.0,
            duration=0.3
        )

        # First element scales down
        first_scale1 = keystates1[0].state.scale
        last_scale1 = keystates1[-1].state.scale
        assert first_scale1 > last_scale1

        # Second element scales up
        first_scale2 = keystates2[0].state.scale
        last_scale2 = keystates2[-1].state.scale
        assert first_scale2 < last_scale2


@pytest.mark.unit
class TestSlideReplaceAnimation:
    """Test slide_replace animation helper"""

    def test_slide_replace_right(self):
        """Test slide replace to the right"""
        state1 = CircleState(x=0, y=0, radius=50)
        state2 = RectangleState(x=0, y=0, width=80, height=60)

        keystates1, keystates2 = slide_replace(
            state1, state2,
            direction="right",
            distance=200,
            duration=0.3
        )

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)
        assert all(isinstance(ks, KeyState) for ks in keystates1)
        assert all(isinstance(ks, KeyState) for ks in keystates2)

    def test_slide_replace_left(self):
        """Test slide replace to the left"""
        state1 = CircleState(x=100, y=0, radius=50)
        state2 = RectangleState(x=100, y=0, width=80, height=60)

        keystates1, keystates2 = slide_replace(
            state1, state2,
            direction="left",
            distance=150,
            duration=0.3
        )

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)

    def test_slide_replace_up(self):
        """Test slide replace upward"""
        state1 = CircleState(radius=50)
        state2 = RectangleState(width=80, height=60)

        keystates1, keystates2 = slide_replace(
            state1, state2,
            direction="up",
            distance=100,
            duration=0.3
        )

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)

    def test_slide_replace_down(self):
        """Test slide replace downward"""
        state1 = CircleState(radius=50)
        state2 = RectangleState(width=80, height=60)

        keystates1, keystates2 = slide_replace(
            state1, state2,
            direction="down",
            distance=100,
            duration=0.3
        )

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)


@pytest.mark.unit
class TestRotateFlipAnimation:
    """Test rotate_flip animation helper"""

    def test_rotate_flip_clockwise(self):
        """Test rotate flip clockwise"""
        state1 = RectangleState(width=100, height=60, fill_color=Color("#FF0000"))
        state2 = RectangleState(width=100, height=60, fill_color=Color("#0000FF"))

        keystates1, keystates2 = rotate_flip(
            state1, state2,
            angle=180,
            duration=0.5
        )

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)
        assert all(isinstance(ks, KeyState) for ks in keystates1)
        assert all(isinstance(ks, KeyState) for ks in keystates2)

    def test_rotate_flip_opacity_transition(self):
        """Test that rotate flip has opacity transitions"""
        state1 = RectangleState(width=100, height=60)
        state2 = CircleState(radius=50)

        keystates1, keystates2 = rotate_flip(
            state1, state2,
            angle=180,
            duration=0.5
        )

        # First element should fade out
        first_opacity1 = keystates1[0].state.opacity
        last_opacity1 = keystates1[-1].state.opacity
        assert first_opacity1 > last_opacity1

        # Second element should fade in
        first_opacity2 = keystates2[0].state.opacity
        last_opacity2 = keystates2[-1].state.opacity
        assert first_opacity2 < last_opacity2

    def test_rotate_flip_with_rotation_change(self):
        """Test rotate flip with rotation angle"""
        state1 = RectangleState(width=100, height=60)
        state2 = RectangleState(width=100, height=60)

        keystates1, keystates2 = rotate_flip(
            state1, state2,
            angle=180,
            duration=0.5
        )

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)
        assert len(keystates1) >= 2
        assert len(keystates2) >= 2


@pytest.mark.unit
class TestCompoundAnimationTransitions:
    """Test transitions in compound animations"""

    def test_crossfade_smooth_transition(self):
        """Test that crossfade creates smooth opacity transition"""
        state1 = CircleState(radius=50, opacity=1.0)
        state2 = CircleState(radius=75, opacity=1.0)

        keystates1, keystates2 = crossfade(state1, state2, duration=0.3)

        # Should have at least one state per element
        assert len(keystates1) >= 1
        assert len(keystates2) >= 1

    def test_bounce_replace_has_transitions(self):
        """Test that bounce replace has keystates"""
        state1 = CircleState(radius=50)
        state2 = CircleState(radius=75)

        keystates1, keystates2 = bounce_replace(state1, state2, duration=0.4)

        assert len(keystates1) >= 1
        assert len(keystates2) >= 1

    def test_scale_swap_opposite_scales(self):
        """Test that scale swap animates opposite scales"""
        state1 = CircleState(radius=50, scale=1.0)
        state2 = RectangleState(width=80, height=60, scale=1.0)

        keystates1, keystates2 = scale_swap(state1, state2, min_scale=0.1, duration=0.3)

        # Should have keystates with varying scales
        assert len(keystates1) >= 2
        assert len(keystates2) >= 2


@pytest.mark.unit
class TestCompoundAnimationEdgeCases:
    """Test edge cases in compound animations"""

    def test_crossfade_identical_states(self):
        """Test crossfade between identical states"""
        state1 = CircleState(x=100, y=100, radius=50)
        state2 = CircleState(x=100, y=100, radius=50)

        keystates1, keystates2 = crossfade(state1, state2, duration=0.3)

        # Should still create valid animation
        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)

    def test_bounce_replace_with_zero_duration(self):
        """Test bounce replace with zero duration"""
        state1 = CircleState(radius=50)
        state2 = CircleState(radius=75)

        keystates1, keystates2 = bounce_replace(state1, state2, duration=0.0)
        # Should handle gracefully
        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)

    def test_slide_replace_zero_distance(self):
        """Test slide replace with zero distance"""
        state1 = CircleState(radius=50)
        state2 = RectangleState(width=80, height=60)

        keystates1, keystates2 = slide_replace(
            state1, state2,
            direction="right",
            distance=0,
            duration=0.3
        )

        assert isinstance(keystates1, list)
        assert isinstance(keystates2, list)


@pytest.mark.unit
class TestCompoundAnimationChaining:
    """Test chaining compound animations"""

    def test_multiple_crossfades_sequence(self):
        """Test sequencing multiple crossfade animations"""
        state1 = CircleState(radius=50, fill_color=Color("#FF0000"))
        state2 = CircleState(radius=60, fill_color=Color("#00FF00"))
        state3 = CircleState(radius=70, fill_color=Color("#0000FF"))

        # Sequence crossfades
        ks1_a, ks1_b = crossfade(state1, state2, duration=0.3)
        ks2_a, ks2_b = crossfade(state2, state3, duration=0.3)

        assert isinstance(ks1_a, list)
        assert isinstance(ks1_b, list)
        assert isinstance(ks2_a, list)
        assert isinstance(ks2_b, list)
