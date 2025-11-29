"""Unit tests for basic interpolation functions"""

import pytest
import math
from vood.transition import lerp, angle, step, inbetween, circular_midpoint
from vood.core.color import Color


@pytest.mark.unit
class TestLerp:
    """Test linear interpolation"""

    def test_lerp_start(self):
        """Test lerp at t=0 returns start value"""
        assert lerp(0, 100, 0.0) == 0

    def test_lerp_end(self):
        """Test lerp at t=1 returns end value"""
        assert lerp(0, 100, 1.0) == 100

    def test_lerp_midpoint(self):
        """Test lerp at t=0.5 returns midpoint"""
        assert lerp(0, 100, 0.5) == 50

    def test_lerp_quarter(self):
        """Test lerp at t=0.25"""
        assert lerp(0, 100, 0.25) == 25

    def test_lerp_negative_values(self):
        """Test lerp with negative values"""
        assert lerp(-100, 100, 0.5) == 0

    def test_lerp_floats(self):
        """Test lerp with float values"""
        result = lerp(0.0, 1.0, 0.333)
        assert abs(result - 0.333) < 0.001

    def test_lerp_reversed(self):
        """Test lerp from higher to lower value"""
        assert lerp(100, 0, 0.5) == 50

    def test_lerp_extrapolation_below(self):
        """Test lerp with t < 0 (extrapolation)"""
        assert lerp(0, 100, -0.5) == -50

    def test_lerp_extrapolation_above(self):
        """Test lerp with t > 1 (extrapolation)"""
        assert lerp(0, 100, 1.5) == 150


@pytest.mark.unit
class TestAngleInterpolation:
    """Test angle interpolation with wraparound handling"""

    def test_angle_no_wraparound(self):
        """Test angle interpolation without wraparound"""
        result = angle(0, 90, 0.5)
        assert abs(result - 45) < 0.001

    def test_angle_wraparound_shortest_path(self):
        """Test angle takes shortest path through 0/360 boundary"""
        # From 350° to 10° should go through 0° (not backwards to 180°)
        result = angle(350, 10, 0.5)
        # Shortest path: 350 -> 360/0 -> 10 (20° total)
        # Midpoint should be 0°/360°
        assert abs(result - 0) < 0.001 or abs(result - 360) < 0.001

    def test_angle_wraparound_reverse(self):
        """Test angle wraparound in reverse direction"""
        # From 10° to 350° should go through 0° (not forward to 180°)
        result = angle(10, 350, 0.5)
        assert abs(result - 0) < 0.001 or abs(result - 360) < 0.001

    def test_angle_180_degree_rotation(self):
        """Test 180° rotation (ambiguous - could go either way)"""
        result = angle(0, 180, 0.5)
        assert abs(result - 90) < 0.001

    def test_angle_full_rotation(self):
        """Test near-full rotation"""
        result = angle(0, 359, 0.5)
        # Library chooses shortest path: 0→359 is -1° (backwards through 0)
        # Midpoint is at -0.5° (still going backwards - shortest path wins)
        assert abs(result - (-0.5)) < 0.001

    def test_angle_negative_values(self):
        """Test angle interpolation with negative angles"""
        result = angle(-45, 45, 0.5)
        # Negative angles are normalized: -45° → 315°
        # Shortest path from 315° to 45° is +90° (going forward)
        # Midpoint: 315° + 90°*0.5 = 360° (equivalent to 0°, but not normalized)
        assert abs(result - 360.0) < 0.001 or abs(result - 0) < 0.001

    def test_angle_same_values(self):
        """Test angle interpolation with identical start/end"""
        assert angle(45, 45, 0.5) == 45


@pytest.mark.unit
class TestStep:
    """Test step function (discrete transition at t=0.5)"""

    def test_step_before_threshold(self):
        """Test step returns start value before threshold"""
        assert step("A", "B", 0.0) == "A"
        assert step("A", "B", 0.49) == "A"

    def test_step_at_threshold(self):
        """Test step returns end value at threshold"""
        assert step("A", "B", 0.5) == "B"

    def test_step_after_threshold(self):
        """Test step returns end value after threshold"""
        assert step("A", "B", 0.51) == "B"
        assert step("A", "B", 1.0) == "B"

    def test_step_with_objects(self):
        """Test step with object values"""
        obj1 = {"value": 1}
        obj2 = {"value": 2}
        assert step(obj1, obj2, 0.3) is obj1
        assert step(obj1, obj2, 0.7) is obj2


@pytest.mark.unit
class TestColorInterpolation:
    """Test color interpolation edge cases"""

    def test_color_interpolation_start(self):
        """Test color interpolation at t=0"""
        color1 = Color("#FF0000")  # Red
        color2 = Color("#0000FF")  # Blue
        result = color1.interpolate(color2, 0.0)
        assert result.r == 255
        assert result.g == 0
        assert result.b == 0

    def test_color_interpolation_end(self):
        """Test color interpolation at t=1"""
        color1 = Color("#FF0000")  # Red
        color2 = Color("#0000FF")  # Blue
        result = color1.interpolate(color2, 1.0)
        assert result.r == 0
        assert result.g == 0
        assert result.b == 255

    def test_color_interpolation_midpoint(self):
        """Test color interpolation at t=0.5"""
        color1 = Color("#FF0000")  # Red
        color2 = Color("#0000FF")  # Blue
        result = color1.interpolate(color2, 0.5)
        # Library uses perceptually uniform color interpolation (LAB color space)
        assert result.r == 202
        assert result.g == 0
        assert result.b == 136

    def test_color_interpolation_with_transparency(self):
        """Test color interpolation with transparent color"""
        color1 = Color("#FF0000")  # Red
        color2 = Color.NONE  # Transparent
        result = color1.interpolate(color2, 0.5)
        # Interpolation with NONE doesn't produce a partially transparent color
        # but returns a solid color
        assert not result.is_none()

    def test_color_interpolation_grayscale(self):
        """Test color interpolation between gray values"""
        color1 = Color("#000000")  # Black
        color2 = Color("#FFFFFF")  # White
        result = color1.interpolate(color2, 0.5)
        # LAB color space interpolation result
        assert result.r == 119
        assert result.g == 119
        assert result.b == 119


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_lerp_identical_values(self):
        """Test lerp with identical start and end"""
        assert lerp(50, 50, 0.5) == 50

    def test_lerp_zero_range(self):
        """Test lerp with zero at both ends"""
        assert lerp(0, 0, 0.5) == 0

    def test_lerp_very_small_values(self):
        """Test lerp with very small float values"""
        result = lerp(1e-10, 1e-9, 0.5)
        assert result > 0

    def test_lerp_very_large_values(self):
        """Test lerp with very large values"""
        result = lerp(1e10, 2e10, 0.5)
        assert abs(result - 1.5e10) < 1e8

    def test_angle_with_multiples_of_360(self):
        """Test angle normalization with multiples of 360"""
        result = angle(0, 720, 0.5)
        # 720° is equivalent to 0°, should return 0°
        assert abs(result - 0) < 0.001

    def test_step_at_exact_boundary(self):
        """Test step function at exact 0.5 boundary"""
        # Should consistently return end value at 0.5
        for _ in range(10):
            assert step(0, 1, 0.5) == 1
