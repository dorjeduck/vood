"""Comprehensive state validation tests for all shape states"""

import pytest
from dataclasses import replace

from vood.core.color import Color
from vood.core.point2d import Point2D
from vood.component.state import (
    # Vertex-based states
    AstroidState,
    CircleState,
    EllipseState,
    HeartState,
    InfinityState,
    LineState,
    PolygonState,
    RectangleState,
    SquareState,
    StarState,
    TriangleState,
    SpiralState,
    WaveState,
    FlowerState,
    # Perforated states
    PolyRingState,
    RingState,
    SquareRingState,
    RadialSegmentsState,
    # Simple states
    ArcState,
    ArrowState,
    CrossState,
    PathState,
    PathTextState,
    CircleTextState,
    RawSvgState,
    TextState,
)


@pytest.mark.unit
class TestVertexBasedStates:
    """Test validation for all vertex-based states"""

    def test_circle_state_creation(self):
        """Test CircleState creation with valid parameters"""
        state = CircleState(x=100, y=100, radius=50)
        assert state.x == 100
        assert state.y == 100
        assert state.radius == 50
        assert state.opacity == 1.0
        assert state.scale == 1.0
        assert state.rotation == 0

    def test_circle_state_immutability(self):
        """Test that CircleState is immutable"""
        state = CircleState(x=100, y=100, radius=50)
        with pytest.raises(AttributeError):
            state.x = 200

    def test_circle_state_replace(self):
        """Test replacing CircleState fields"""
        state = CircleState(x=100, y=100, radius=50)
        new_state = replace(state, x=200, radius=75)
        assert new_state.x == 200
        assert new_state.radius == 75
        assert new_state.y == 100  # Unchanged
        assert state.x == 100  # Original unchanged

    def test_ellipse_state_creation(self):
        """Test EllipseState creation"""
        state = EllipseState(x=100, y=100, rx=80, ry=50)
        assert state.rx == 80
        assert state.ry == 50

    def test_rectangle_state_creation(self):
        """Test RectangleState creation"""
        state = RectangleState(x=100, y=100, width=150, height=80)
        assert state.width == 150
        assert state.height == 80

    def test_square_state_creation(self):
        """Test SquareState creation"""
        state = SquareState(x=100, y=100, size=100)
        assert state.size == 100

    def test_triangle_state_creation(self):
        """Test TriangleState creation"""
        state = TriangleState(x=100, y=100, size=100)
        assert state.size == 100

    def test_polygon_state_creation(self):
        """Test PolygonState creation"""
        state = PolygonState(x=100, y=100, size=50, num_sides=6)
        assert state.size == 50
        assert state.num_sides == 6

    def test_star_state_creation(self):
        """Test StarState creation"""
        state = StarState(
            x=100, y=100, outer_radius=80, inner_radius=40, num_points_star=5
        )
        assert state.outer_radius == 80
        assert state.inner_radius == 40
        assert state.num_points_star == 5

    def test_line_state_creation(self):
        """Test LineState creation"""
        state = LineState(length=100)
        assert state.length == 100

    def test_astroid_state_creation(self):
        """Test AstroidState creation"""
        state = AstroidState(x=100, y=100, radius=50)
        assert state.radius == 50

    def test_heart_state_creation(self):
        """Test HeartState creation"""
        state = HeartState(x=100, y=100, size=50)
        assert state.size == 50

    def test_infinity_state_creation(self):
        """Test InfinityState creation"""
        state = InfinityState(x=100, y=100, size=50)
        assert state.size == 50

    def test_spiral_state_creation(self):
        """Test SpiralState creation"""
        state = SpiralState(x=100, y=100, start_radius=10, end_radius=100, turns=3)
        assert state.start_radius == 10
        assert state.end_radius == 100
        assert state.turns == 3

    def test_wave_state_creation(self):
        """Test WaveState creation"""
        state = WaveState(x=100, y=100, length=200, amplitude=30, frequency=2)
        assert state.length == 200
        assert state.amplitude == 30
        assert state.frequency == 2

    def test_flower_state_creation(self):
        """Test FlowerState creation"""
        state = FlowerState(x=100, y=100, size=50, num_petals=6)
        assert state.size == 50
        assert state.num_petals == 6


@pytest.mark.unit
class TestPerforatedStates:
    """Test validation for perforated (hollow) states"""

    def test_ring_state_creation(self):
        """Test RingState creation"""
        state = RingState(x=100, y=100, outer_radius=80, inner_radius=50)
        assert state.outer_radius == 80
        assert state.inner_radius == 50

    def test_poly_ring_state_creation(self):
        """Test PolyRingState creation"""
        state = PolyRingState(x=100, y=100, outer_size=80, inner_size=50, num_edges=6)
        assert state.outer_size == 80
        assert state.inner_size == 50
        assert state.num_edges == 6

    def test_square_ring_state_creation(self):
        """Test SquareRingState creation"""
        state = SquareRingState(x=100, y=100, outer_size=100, inner_size=60)
        assert state.outer_size == 100
        assert state.inner_size == 60

    def test_radial_segments_state_creation(self):
        """Test RadialSegmentsState creation"""
        state = RadialSegmentsState(x=100, y=100, num_lines=8)
        assert state.num_lines == 8


@pytest.mark.unit
class TestSimpleStates:
    """Test validation for simple (non-vertex) states"""

    def test_text_state_creation(self):
        """Test TextState creation"""
        state = TextState(x=100, y=100, text="Hello", font_size=24)
        assert state.text == "Hello"
        assert state.font_size == 24

    def test_arc_state_creation(self):
        """Test ArcState creation"""
        state = ArcState(x=100, y=100, radius=50, start_angle=0, end_angle=180)
        assert state.radius == 50
        assert state.start_angle == 0
        assert state.end_angle == 180

    def test_arrow_state_creation(self):
        """Test ArrowState creation"""
        state = ArrowState(length=100, head_width=10, head_length=15)
        assert state.length == 100
        assert state.head_width == 10
        assert state.head_length == 15

    def test_cross_state_creation(self):
        """Test CrossState creation"""
        state = CrossState(x=100, y=100, width=50, thickness=10)
        assert state.width == 50
        assert state.thickness == 10

    def test_path_state_creation(self):
        """Test PathState creation"""
        state = PathState(x=0, y=0, data="M 0 0 L 100 100")
        # data is converted to SVGPath object internally
        assert state.data is not None

    # Note: ImageState not yet implemented in main codebase
    # def test_image_state_creation(self):
    #     """Test ImageState creation"""
    #     state = ImageState(
    #         x=100, y=100,
    #         image_path="/path/to/image.png",
    #         width=200,
    #         height=150
    #     )
    #     assert state.image_path == "/path/to/image.png"
    #     assert state.width == 200
    #     assert state.height == 150

    def test_raw_svg_state_creation(self):
        """Test RawSvgState creation"""
        svg_content = '<circle cx="50" cy="50" r="40"/>'
        state = RawSvgState(x=0, y=0, svg_data=svg_content)
        assert state.svg_data == svg_content


@pytest.mark.unit
class TestStateCommonProperties:
    """Test common properties across all states"""

    @pytest.mark.parametrize(
        "state_class,kwargs",
        [
            (CircleState, {"radius": 50}),
            (RectangleState, {"width": 100, "height": 60}),
            (TriangleState, {"size": 100}),
            (TextState, {"text": "Test"}),
        ],
    )
    def test_common_position_properties(self, state_class, kwargs):
        """Test that all states have x, y position properties"""
        state = state_class(x=123, y=456, **kwargs)
        assert state.x == 123
        assert state.y == 456

    @pytest.mark.parametrize(
        "state_class,kwargs",
        [
            (CircleState, {"radius": 50}),
            (RectangleState, {"width": 100, "height": 60}),
            (TriangleState, {"size": 100}),
            (TextState, {"text": "Test"}),
        ],
    )
    def test_common_transform_properties(self, state_class, kwargs):
        """Test that all states have scale, rotation, opacity"""
        state = state_class(x=0, y=0, scale=2.5, rotation=45, opacity=0.7, **kwargs)
        assert state.scale == 2.5
        assert state.rotation == 45
        assert state.opacity == 0.7

    @pytest.mark.parametrize(
        "state_class,kwargs",
        [
            (CircleState, {"radius": 50}),
            (RectangleState, {"width": 100, "height": 60}),
            (PolygonState, {"size": 50, "num_sides": 6}),
        ],
    )
    def test_common_visual_properties(self, state_class, kwargs):
        """Test that vertex states have fill_color, stroke_color, stroke_width"""
        state = state_class(
            x=0,
            y=0,
            fill_color=Color("#FF0000"),
            stroke_color=Color("#0000FF"),
            stroke_width=3.5,
            **kwargs,
        )
        assert state.fill_color == Color("#FF0000")
        assert state.stroke_color == Color("#0000FF")
        assert state.stroke_width == 3.5


@pytest.mark.unit
class TestStateDefaultValues:
    """Test default values for state properties"""

    def test_circle_defaults(self):
        """Test CircleState default values"""
        state = CircleState()
        assert state.x == 0
        assert state.y == 0
        assert state.radius == 50
        assert state.scale == 1.0
        assert state.opacity == 1.0
        assert state.rotation == 0
        assert state.fill_color is not None
        assert state.stroke_width >= 0

    def test_text_defaults(self):
        """Test TextState default values"""
        state = TextState(text="Test")
        assert state.x == 0
        assert state.y == 0
        assert state.font_size > 0
        assert state.opacity == 1.0


@pytest.mark.unit
class TestStateColorHandling:
    """Test color property handling in states"""

    def test_color_assignment_from_hex(self):
        """Test assigning color from hex string"""
        state = CircleState(fill_color=Color("#FF0000"))
        assert state.fill_color.r == 255
        assert state.fill_color.g == 0
        assert state.fill_color.b == 0

    def test_color_assignment_from_rgb(self):
        """Test assigning color from RGB values"""
        state = CircleState(fill_color=Color(128, 64, 32))
        assert state.fill_color.r == 128
        assert state.fill_color.g == 64
        assert state.fill_color.b == 32

    def test_color_none_transparent(self):
        """Test Color.NONE for transparency"""
        state = CircleState(fill_color=Color.NONE)
        assert state.fill_color.is_none()

    def test_color_interpolation_compatibility(self):
        """Test that colors can be interpolated"""
        color1 = Color("#FF0000")
        color2 = Color("#0000FF")
        mid_color = color1.interpolate(color2, 0.5)
        # Red to Blue midpoint should have red and blue components
        assert mid_color.r > 0
        assert mid_color.b > 0


@pytest.mark.unit
class TestStateValidation:
    """Test parameter validation in states"""

    def test_negative_radius_allowed(self):
        """Test that negative radius is allowed (for animations)"""
        # Negative values should be allowed for smooth transitions
        state = CircleState(radius=-10)
        assert state.radius == -10

    def test_zero_dimensions_allowed(self):
        """Test that zero dimensions are allowed"""
        state = RectangleState(width=0, height=0)
        assert state.width == 0
        assert state.height == 0

    def test_opacity_clamping_not_enforced(self):
        """Test that opacity values outside [0, 1] are allowed"""
        # Values outside [0, 1] allowed for animation overshoot
        state = CircleState(opacity=1.5)
        assert state.opacity == 1.5

        state2 = CircleState(opacity=-0.1)
        assert state2.opacity == -0.1


@pytest.mark.unit
class TestStateGeneration:
    """Test state generation methods for vertex-based states"""

    def test_circle_generates_contours(self):
        """Test that CircleState generates vertex contours"""
        state = CircleState(radius=50, _num_vertices=8)
        contours = state._generate_contours()

        assert contours.outer is not None
        assert len(contours.outer.vertices) == 8
        assert contours.outer.closed is True
        assert len(contours.holes) == 0

    def test_rectangle_generates_contours(self):
        """Test that RectangleState generates vertex contours"""
        state = RectangleState(width=100, height=60, _num_vertices=4)
        contours = state._generate_contours()

        assert contours.outer is not None
        assert len(contours.outer.vertices) == 4
        assert contours.outer.closed is True

    def test_ring_generates_contours_with_hole(self):
        """Test that RingState generates contours with hole"""
        state = RingState(outer_radius=100, inner_radius=50, _num_vertices=8)
        contours = state._generate_contours()

        assert contours.outer is not None
        assert len(contours.holes) == 1
        assert contours.holes[0].closed is True

    def test_poly_ring_generates_contours_with_hole(self):
        """Test that PolyRingState generates contours with hole"""
        state = PolyRingState(
            outer_size=100, inner_size=50, num_edges=6, _num_vertices=24
        )
        contours = state._generate_contours()

        assert contours.outer is not None
        assert len(contours.holes) == 1


@pytest.mark.unit
class TestStateEquality:
    """Test state equality comparisons"""

    def test_identical_states_equal(self):
        """Test that identical states are equal"""
        state1 = CircleState(x=100, y=100, radius=50)
        state2 = CircleState(x=100, y=100, radius=50)
        assert state1 == state2

    def test_different_values_not_equal(self):
        """Test that states with different values are not equal"""
        state1 = CircleState(x=100, y=100, radius=50)
        state2 = CircleState(x=100, y=100, radius=75)
        assert state1 != state2

    def test_different_types_not_equal(self):
        """Test that different state types are not equal"""
        state1 = CircleState(x=100, y=100, radius=50)
        state2 = RectangleState(x=100, y=100, width=100, height=100)
        assert state1 != state2


@pytest.mark.unit
class TestStateHashing:
    """Test state hashing for use in dictionaries/sets"""

    def test_state_hashable(self):
        """Test that states can be used as dictionary keys"""
        state1 = CircleState(x=100, y=100, radius=50)
        state2 = CircleState(x=100, y=100, radius=50)
        state3 = CircleState(x=200, y=200, radius=75)

        state_dict = {state1: "first", state3: "second"}
        assert state_dict[state2] == "first"  # state1 == state2
        assert state_dict[state3] == "second"

    def test_state_in_set(self):
        """Test that states can be added to sets"""
        state1 = CircleState(x=100, y=100, radius=50)
        state2 = CircleState(x=100, y=100, radius=50)
        state3 = CircleState(x=200, y=200, radius=75)

        state_set = {state1, state2, state3}
        # state1 and state2 are equal, so set should have 2 elements
        assert len(state_set) == 2
