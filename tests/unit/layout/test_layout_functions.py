"""Tests for layout functions"""

import pytest
import math

from vood.component.state import CircleState, RectangleState, TextState
from vood import layout


@pytest.mark.unit
class TestCircleLayout:
    """Test circle layout function"""

    def test_circle_layout_basic(self):
        """Test basic circle layout"""
        states = [CircleState(radius=10) for _ in range(8)]
        positioned = layout.circle(states, radius=100)

        assert len(positioned) == 8
        for state in positioned:
            # Check states were positioned
            distance = math.sqrt(state.x**2 + state.y**2)
            assert abs(distance - 100) < 1.0  # Should be on circle

    def test_circle_layout_empty_list(self):
        """Test circle layout with empty list"""
        positioned = layout.circle([], radius=100)
        assert len(positioned) == 0

    def test_circle_layout_single_element(self):
        """Test circle layout with single element"""
        states = [CircleState(radius=10)]
        positioned = layout.circle(states, radius=100)

        assert len(positioned) == 1
        # Single element should be positioned at angle 0 (top, y=-radius)
        assert positioned[0].y == pytest.approx(-100, abs=1.0)

    def test_circle_layout_custom_center(self):
        """Test circle layout with custom center"""
        states = [CircleState(radius=10) for _ in range(4)]
        positioned = layout.circle(states, radius=50, cx=200, cy=300)

        for state in positioned:
            # Check states are centered around (200, 300)
            distance = math.sqrt((state.x - 200) ** 2 + (state.y - 300) ** 2)
            assert abs(distance - 50) < 1.0

    def test_circle_layout_rotation(self):
        """Test circle layout with rotation"""
        states = [CircleState(radius=10) for _ in range(4)]
        positioned = layout.circle(states, radius=100, rotation=90)

        # First element should be at 90 degrees (East)
        assert positioned[0].x == pytest.approx(100, abs=1.0)
        assert positioned[0].y == pytest.approx(0, abs=1.0)


@pytest.mark.unit
class TestEllipseLayout:
    """Test ellipse layout function"""

    def test_ellipse_layout_basic(self):
        """Test basic ellipse layout"""
        states = [CircleState(radius=10) for _ in range(6)]
        positioned = layout.ellipse(states, rx=150, ry=80)

        assert len(positioned) == 6
        # Verify elements are on ellipse
        for state in positioned:
            # Ellipse equation: (x/a)^2 + (y/b)^2 = 1
            normalized = (state.x / 150) ** 2 + (state.y / 80) ** 2
            assert abs(normalized - 1.0) < 0.01

    def test_ellipse_layout_circular_when_equal_radii(self):
        """Test that ellipse becomes circle when radii are equal"""
        states = [CircleState(radius=10) for _ in range(8)]
        positioned = layout.ellipse(states, rx=100, ry=100)

        for state in positioned:
            distance = math.sqrt(state.x**2 + state.y**2)
            assert abs(distance - 100) < 1.0


@pytest.mark.unit
class TestLineLayout:
    """Test line layout function"""

    def test_line_layout_basic(self):
        """Test basic line layout"""
        states = [CircleState(radius=5) for _ in range(5)]
        positioned = layout.line(states, spacing=100, rotation=0, cx=0, cy=0)

        assert len(positioned) == 5
        # Elements should be evenly spaced along horizontal line
        assert positioned[0].x == pytest.approx(-200)
        assert positioned[4].x == pytest.approx(200)
        assert all(s.y == pytest.approx(0) for s in positioned)

    def test_line_layout_diagonal(self):
        """Test line layout on diagonal"""
        states = [CircleState(radius=5) for _ in range(3)]
        positioned = layout.line(states, spacing=100, rotation=45, cx=0, cy=0)

        assert len(positioned) == 3
        # Middle element should be at center
        assert positioned[1].x == pytest.approx(0, abs=0.1)
        assert positioned[1].y == pytest.approx(0, abs=0.1)

    def test_line_layout_single_element(self):
        """Test line layout with single element"""
        states = [CircleState(radius=5)]
        positioned = layout.line(states, spacing=100, rotation=0, cx=0, cy=0)

        # Single element should be at center
        assert positioned[0].x == pytest.approx(0)
        assert positioned[0].y == pytest.approx(0)


@pytest.mark.unit
class TestGridLayout:
    """Test grid layout function"""

    def test_grid_layout_basic(self):
        """Test basic grid layout"""
        states = [CircleState(radius=5) for _ in range(12)]
        positioned = layout.grid(states, rows=3, cols=4, spacing_h=50, spacing_v=50)

        assert len(positioned) == 12

        # Check first element (top-left, centered at grid center)
        # Grid is centered at (0,0), so first element offset is -(cols-1)/2 * spacing_h, -(rows-1)/2 * spacing_v
        expected_x0 = -(4 - 1) * 50 / 2
        expected_y0 = -(3 - 1) * 50 / 2
        assert positioned[0].x == pytest.approx(expected_x0)
        assert positioned[0].y == pytest.approx(expected_y0)

        # Check spacing is correct
        assert positioned[1].x == pytest.approx(positioned[0].x + 50)  # Next column
        assert positioned[4].y == pytest.approx(positioned[0].y + 50)  # Next row

    def test_grid_layout_single_row(self):
        """Test grid layout with single row"""
        states = [CircleState(radius=5) for _ in range(4)]
        positioned = layout.grid(states, rows=1, cols=4, spacing_h=50, spacing_v=50)

        assert len(positioned) == 4
        # All should have same y
        assert all(s.y == 0 for s in positioned)

    def test_grid_layout_single_column(self):
        """Test grid layout with single column"""
        states = [CircleState(radius=5) for _ in range(4)]
        positioned = layout.grid(states, rows=4, cols=1, spacing_h=50, spacing_v=50)

        assert len(positioned) == 4
        # All should have same x
        assert all(s.x == 0 for s in positioned)

    def test_grid_layout_partial_last_row(self):
        """Test grid layout with partial last row"""
        states = [CircleState(radius=5) for _ in range(10)]
        positioned = layout.grid(states, rows=3, cols=4, spacing_h=50, spacing_v=50)

        # Should still position all 10 elements
        assert len(positioned) == 10


@pytest.mark.unit
class TestRadialGridLayout:
    """Test radial grid layout function"""

    def test_radial_grid_layout_basic(self):
        """Test basic radial grid layout"""
        states = [CircleState(radius=5) for _ in range(12)]
        positioned = layout.radial_grid(states, rings=3, segments=4, ring_spacing=50)

        assert len(positioned) == 12

    def test_radial_grid_layout_single_ring(self):
        """Test radial grid with single ring"""
        states = [CircleState(radius=5) for _ in range(8)]
        positioned = layout.radial_grid(states, rings=1, segments=8, ring_spacing=50)

        assert len(positioned) == 8
        # All should be at same distance from center
        distances = [math.sqrt(s.x**2 + s.y**2) for s in positioned]
        assert all(abs(d - distances[0]) < 1.0 for d in distances)


@pytest.mark.unit
class TestPolygonLayout:
    """Test polygon layout function"""

    def test_polygon_layout_triangle(self):
        """Test polygon layout with 3 sides (triangle)"""
        states = [CircleState(radius=5) for _ in range(3)]
        positioned = layout.polygon(states, radius=100, sides=3)

        assert len(positioned) == 3
        # All should be at distance 100 from center
        for state in positioned:
            distance = math.sqrt(state.x**2 + state.y**2)
            assert abs(distance - 100) < 1.0

    def test_polygon_layout_hexagon(self):
        """Test polygon layout with 6 sides"""
        states = [CircleState(radius=5) for _ in range(6)]
        positioned = layout.polygon(states, radius=100, sides=6)

        assert len(positioned) == 6


@pytest.mark.unit
class TestSpiralLayout:
    """Test spiral layout function"""

    def test_spiral_layout_basic(self):
        """Test basic spiral layout"""
        states = [CircleState(radius=5) for _ in range(20)]
        positioned = layout.spiral(
            states,
            start_radius=10,
            radius_step=10,
            angle_step=54,  # 360 * 3 turns / 20 elements
        )

        assert len(positioned) == 20

        # First element should be near inner radius
        first_distance = math.sqrt(positioned[0].x ** 2 + positioned[0].y ** 2)
        assert first_distance < 50

        # Last element should be near outer radius
        last_distance = math.sqrt(positioned[-1].x ** 2 + positioned[-1].y ** 2)
        assert last_distance > 150

    def test_spiral_layout_increasing_radius(self):
        """Test that spiral radius increases"""
        states = [CircleState(radius=5) for _ in range(10)]
        positioned = layout.spiral(
            states,
            start_radius=20,
            radius_step=20,
            angle_step=72,  # 360 * 2 turns / 10 elements
        )

        # Calculate distances from center
        distances = [math.sqrt(s.x**2 + s.y**2) for s in positioned]

        # Distances should generally increase
        # (allow some deviation for spiral geometry)
        assert distances[-1] > distances[0]


@pytest.mark.unit
class TestWaveLayout:
    """Test wave layout function"""

    def test_wave_layout_basic(self):
        """Test basic wave layout"""
        states = [CircleState(radius=5) for _ in range(20)]
        positioned = layout.wave(states, amplitude=50, wavelength=200, spacing=20)

        assert len(positioned) == 20

        # x coordinates should span approximately 380 (19 * 20 spacing)
        x_coords = [s.x for s in positioned]
        assert max(x_coords) - min(x_coords) == pytest.approx(380, abs=1)

        # y coordinates should vary (wave motion)
        y_coords = [s.y for s in positioned]
        amplitude_test = 50
        assert max(y_coords) - min(y_coords) > amplitude_test

    def test_wave_layout_zero_amplitude(self):
        """Test wave layout with zero amplitude (straight line)"""
        states = [CircleState(radius=5) for _ in range(10)]
        positioned = layout.wave(states, amplitude=0, wavelength=200, spacing=25)

        # All y coordinates should be the same
        y_coords = [s.y for s in positioned]
        assert all(y == y_coords[0] for y in y_coords)


@pytest.mark.unit
class TestScatterLayout:
    """Test scatter layout function"""

    def test_scatter_layout_basic(self):
        """Test basic scatter layout"""
        states = [CircleState(radius=5) for _ in range(30)]
        positioned = layout.scatter(
            states,
            x_range=(-200, 200),
            y_range=(-150, 150),
            seed=42,  # Fixed seed for reproducibility
        )

        assert len(positioned) == 30

        # All positions should be within bounds
        for state in positioned:
            assert -200 <= state.x <= 200
            assert -150 <= state.y <= 150

    def test_scatter_layout_reproducible_with_seed(self):
        """Test that scatter layout is reproducible with same seed"""
        states1 = [CircleState(radius=5) for _ in range(10)]
        states2 = [CircleState(radius=5) for _ in range(10)]

        positioned1 = layout.scatter(
            states1, x_range=(-100, 100), y_range=(-100, 100), seed=123
        )
        positioned2 = layout.scatter(
            states2, x_range=(-100, 100), y_range=(-100, 100), seed=123
        )

        # Should produce same positions
        for s1, s2 in zip(positioned1, positioned2):
            assert s1.x == s2.x
            assert s1.y == s2.y

    def test_scatter_layout_different_with_different_seed(self):
        """Test that scatter layout differs with different seed"""
        states1 = [CircleState(radius=5) for _ in range(10)]
        states2 = [CircleState(radius=5) for _ in range(10)]

        positioned1 = layout.scatter(
            states1, x_range=(-100, 100), y_range=(-100, 100), seed=1
        )
        positioned2 = layout.scatter(
            states2, x_range=(-100, 100), y_range=(-100, 100), seed=2
        )

        # Should produce different positions
        different = any(
            s1.x != s2.x or s1.y != s2.y for s1, s2 in zip(positioned1, positioned2)
        )
        assert different


@pytest.mark.unit
class TestBezierLayout:
    """Test bezier layout function"""

    def test_bezier_layout_linear(self):
        """Test bezier layout with linear path (two control points)"""
        from vood.core.point2d import Point2D

        states = [CircleState(radius=5) for _ in range(5)]
        positioned = layout.bezier(
            states, control_points=[Point2D(0, 0), Point2D(100, 100)]
        )

        assert len(positioned) == 5
        # Should be along straight line
        assert positioned[0].x == pytest.approx(0)
        assert positioned[0].y == pytest.approx(0)
        assert positioned[4].x == pytest.approx(100)
        assert positioned[4].y == pytest.approx(100)

    def test_bezier_layout_quadratic(self):
        """Test bezier layout with quadratic curve"""
        from vood.core.point2d import Point2D

        states = [CircleState(radius=5) for _ in range(10)]
        positioned = layout.bezier(
            states, control_points=[Point2D(0, 0), Point2D(50, 100), Point2D(100, 0)]
        )

        assert len(positioned) == 10
        # Middle elements should have higher y values (curve)
        y_coords = [s.y for s in positioned]
        assert max(y_coords) > 0

    def test_bezier_layout_cubic(self):
        """Test bezier layout with cubic curve"""
        from vood.core.point2d import Point2D

        states = [CircleState(radius=5) for _ in range(10)]
        positioned = layout.bezier(
            states,
            control_points=[
                Point2D(0, 0),
                Point2D(33, 100),
                Point2D(66, -100),
                Point2D(100, 0),
            ],
        )

        assert len(positioned) == 10


@pytest.mark.unit
class TestLayoutPreservesProperties:
    """Test that layouts preserve non-position properties"""

    def test_layout_preserves_radius(self):
        """Test that layout preserves radius property"""
        states = [CircleState(radius=i * 10) for i in range(1, 6)]
        positioned = layout.circle(states, radius=100)

        for i, state in enumerate(positioned):
            assert state.radius == (i + 1) * 10

    def test_layout_preserves_colors(self):
        """Test that layout preserves color properties"""
        from vood.core.color import Color

        states = [
            CircleState(
                radius=10,
                fill_color=Color(255, i * 50, 0),
                stroke_color=Color(0, 0, 255),
            )
            for i in range(5)
        ]
        positioned = layout.grid(states, rows=1, cols=5, spacing_h=50, spacing_v=0)

        for i, state in enumerate(positioned):
            assert state.fill_color.r == 255
            assert state.fill_color.g == i * 50
            assert state.stroke_color.b == 255

    def test_layout_preserves_opacity_and_rotation(self):
        """Test that layout preserves opacity and rotation"""
        states = [
            RectangleState(width=50, height=30, opacity=i * 0.2, rotation=i * 30)
            for i in range(5)
        ]
        positioned = layout.line(states, spacing=100, rotation=0, cx=0, cy=0)

        for i, state in enumerate(positioned):
            assert state.opacity == i * 0.2
            assert state.rotation == i * 30

    def test_layout_with_mixed_state_types(self):
        """Test that layout works with mixed state types"""
        states = [
            CircleState(radius=20),
            RectangleState(width=40, height=40),
            RectangleState(
                width=40, height=40
            ),  # Changed TriangleState to RectangleState (not available)
            TextState(text="A"),
        ]
        positioned = layout.grid(states, rows=2, cols=2, spacing_h=100, spacing_v=100)

        assert len(positioned) == 4
        assert isinstance(positioned[0], CircleState)
        assert isinstance(positioned[1], RectangleState)
        assert isinstance(positioned[2], RectangleState)
        assert isinstance(positioned[3], TextState)


@pytest.mark.unit
class TestLayoutEdgeCases:
    """Test edge cases in layout functions"""

    def test_layout_with_zero_spacing(self):
        """Test grid layout with zero spacing"""
        states = [CircleState(radius=5) for _ in range(4)]
        positioned = layout.grid(states, rows=2, cols=2, spacing_h=0, spacing_v=0)

        # All elements should be at origin
        assert all(s.x == 0 for s in positioned[:2])
        assert all(s.y == 0 for s in positioned[::2])

    def test_layout_with_negative_spacing(self):
        """Test grid layout with negative spacing (overlap)"""
        states = [CircleState(radius=5) for _ in range(4)]
        positioned = layout.grid(states, rows=2, cols=2, spacing_h=-20, spacing_v=-20)

        # Elements should overlap
        assert positioned[1].x < positioned[0].x
        assert positioned[2].y < positioned[0].y
