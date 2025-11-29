"""Performance benchmarks for critical operations

These benchmarks track performance over time to detect regressions.
Run with: pytest tests/benchmark -v --benchmark-only
"""

import pytest
from vood.velement import VElement
from vood.vscene import VScene
from vood.component.state.circle import CircleState
from vood.component.state.rectangle import RectangleState
from vood.component.vertex.vertex_loop import VertexLoop
from vood.component.vertex.vertex_contours import VertexContours
from vood.transition.interpolation_engine import InterpolationEngine
from vood.transition.easing_resolver import EasingResolver
from vood.transition.hole_mapping import GreedyNearestMapper
from vood.transition.vertex_alignment import (
    AngularAligner,
    AlignmentContext,
)
from vood.core.color import Color
from vood.core.point2d import Point2D


@pytest.mark.benchmark
class TestInterpolationPerformance:
    """Benchmark interpolation operations"""

    def test_state_interpolation_simple(self, benchmark):
        """Benchmark simple state interpolation"""
        easing_resolver = EasingResolver(property_easing={})
        engine = InterpolationEngine(easing_resolver)

        state1 = CircleState(x=0, y=0, radius=50)
        state2 = CircleState(x=100, y=100, radius=100)

        result = benchmark(
            engine.create_eased_state,
            state1,
            state2,
            0.5,
            segment_easing_overrides=None,
            property_keystates_fields=set(),
        )
        assert result is not None

    def test_state_interpolation_with_colors(self, benchmark):
        """Benchmark state interpolation with color values"""
        easing_resolver = EasingResolver(property_easing={})
        engine = InterpolationEngine(easing_resolver)

        state1 = CircleState(
            x=0,
            y=0,
            radius=50,
            fill_color=Color("#FF0000"),
            stroke_color=Color("#000000"),
        )
        state2 = CircleState(
            x=100,
            y=100,
            radius=100,
            fill_color=Color("#0000FF"),
            stroke_color=Color("#FFFFFF"),
        )

        result = benchmark(
            engine.create_eased_state,
            state1,
            state2,
            0.5,
            segment_easing_overrides=None,
            property_keystates_fields=set(),
        )
        assert result is not None

    def test_vertex_interpolation_no_buffer(self, benchmark):
        """Benchmark vertex interpolation without buffer optimization"""
        easing_resolver = EasingResolver(property_easing={})
        engine = InterpolationEngine(easing_resolver)

        # Create vertex contours with 128 vertices
        vertices1 = [Point2D(i, 0) for i in range(128)]
        vertices2 = [Point2D(i, 100) for i in range(128)]

        loop1 = VertexLoop(vertices1, closed=True)
        loop2 = VertexLoop(vertices2, closed=True)

        contours1 = VertexContours(outer=loop1, holes=[])
        contours2 = VertexContours(outer=loop2, holes=[])

        result = benchmark(
            engine.interpolate_value,
            start_state=CircleState(x=0, y=0, radius=50),
            end_state=CircleState(x=0, y=0, radius=50),
            field_name="_aligned_contours",
            start_value=contours1,
            end_value=contours2,
            eased_t=0.5,
            vertex_buffer=None,
        )
        assert result is not None

    def test_vertex_interpolation_with_buffer(self, benchmark):
        """Benchmark vertex interpolation with buffer optimization"""
        easing_resolver = EasingResolver(property_easing={})
        engine = InterpolationEngine(easing_resolver)

        # Create vertex contours with 128 vertices
        vertices1 = [Point2D(i, 0) for i in range(128)]
        vertices2 = [Point2D(i, 100) for i in range(128)]

        loop1 = VertexLoop(vertices1, closed=True)
        loop2 = VertexLoop(vertices2, closed=True)

        contours1 = VertexContours(outer=loop1, holes=[])
        contours2 = VertexContours(outer=loop2, holes=[])

        # Pre-allocate buffer
        outer_buffer = [Point2D(0, 0) for _ in range(128)]
        vertex_buffer = (outer_buffer, [])

        result = benchmark(
            engine.interpolate_value,
            start_state=CircleState(x=0, y=0, radius=50),
            end_state=CircleState(x=0, y=0, radius=50),
            field_name="_aligned_contours",
            start_value=contours1,
            end_value=contours2,
            eased_t=0.5,
            vertex_buffer=vertex_buffer,
        )
        assert result is not None


@pytest.mark.benchmark
class TestHoleMappingPerformance:
    """Benchmark hole mapping operations"""

    def create_hole_at(self, x, y, size=10):
        """Helper to create a small square hole"""
        vertices = [
            Point2D(x, y),
            Point2D(x + size, y),
            Point2D(x + size, y + size),
            Point2D(x, y + size),
            Point2D(x, y),
        ]
        return VertexLoop(vertices, closed=True)

    def test_hole_mapping_equal_counts(self, benchmark):
        """Benchmark hole mapping with equal counts (N=M)"""
        mapper = GreedyNearestMapper()

        holes1 = [self.create_hole_at(i * 20, i * 20) for i in range(10)]
        holes2 = [self.create_hole_at(i * 20 + 5, i * 20 + 5) for i in range(10)]

        result = benchmark(mapper.map, holes1, holes2)
        assert len(result[0]) == len(result[1])

    def test_hole_mapping_unequal_counts(self, benchmark):
        """Benchmark hole mapping with unequal counts (N>M)"""
        mapper = GreedyNearestMapper()

        holes1 = [self.create_hole_at(i * 20, i * 20) for i in range(20)]
        holes2 = [self.create_hole_at(i * 20, i * 20) for i in range(10)]

        result = benchmark(mapper.map, holes1, holes2)
        assert len(result[0]) == len(result[1])

    def test_hole_mapping_many_holes(self, benchmark):
        """Benchmark hole mapping with many holes"""
        mapper = GreedyNearestMapper()

        holes1 = [self.create_hole_at(i * 10, (i * 7) % 200) for i in range(50)]
        holes2 = [self.create_hole_at((i * 13) % 200, i * 10) for i in range(50)]

        result = benchmark(mapper.map, holes1, holes2)
        assert len(result[0]) == len(result[1])


@pytest.mark.benchmark
class TestVertexAlignmentPerformance:
    """Benchmark vertex alignment operations"""

    def test_angular_alignment(self, benchmark):
        """Benchmark angular alignment for closed shapes"""
        aligner = AngularAligner()

        # Create two squares with different starting vertices
        verts1 = [
            Point2D(50, 50),
            Point2D(-50, 50),
            Point2D(-50, -50),
            Point2D(50, -50),
            Point2D(50, 50),
        ]
        verts2 = [
            Point2D(-50, 50),
            Point2D(-50, -50),
            Point2D(50, -50),
            Point2D(50, 50),
            Point2D(-50, 50),
        ]

        context = AlignmentContext(closed1=True, closed2=True)

        result = benchmark(aligner.align, verts1, verts2, context)
        assert len(result[0]) == len(result[1])

    def test_angular_alignment_many_vertices(self, benchmark):
        """Benchmark angular alignment with many vertices"""
        aligner = AngularAligner()
        import math

        # Create circles with 128 vertices
        n = 128
        verts1 = [
            Point2D(
                100 * math.cos(2 * math.pi * i / n), 100 * math.sin(2 * math.pi * i / n)
            )
            for i in range(n + 1)
        ]
        verts2 = [
            Point2D(
                100 * math.cos(2 * math.pi * i / n + 0.1),
                100 * math.sin(2 * math.pi * i / n + 0.1),
            )
            for i in range(n + 1)
        ]

        context = AlignmentContext(closed1=True, closed2=True)

        result = benchmark(aligner.align, verts1, verts2, context)
        assert len(result[0]) == len(result[1])


@pytest.mark.benchmark
class TestVElementPerformance:
    """Benchmark VElement operations"""

    def test_velement_single_frame(self, benchmark):
        """Benchmark generating single frame from VElement"""
        states = [
            CircleState(x=0, y=0, radius=50),
            CircleState(x=100, y=100, radius=100),
        ]
        element = VElement(keystates=states)

        result = benchmark(element.get_frame, 0.5)
        assert result is not None

    def test_velement_many_keystates(self, benchmark):
        """Benchmark VElement with many keystates"""
        states = [CircleState(x=i * 10, y=i * 10, radius=50 + i) for i in range(20)]
        element = VElement(keystates=states)

        result = benchmark(element.get_frame, 0.5)
        assert result is not None

    def test_velement_with_property_keystates(self, benchmark):
        """Benchmark VElement with property keystate overrides"""
        states = [
            CircleState(x=0, y=0, radius=50),
            CircleState(x=100, y=100, radius=50),
        ]

        property_keystates = {
            "fill_color": [
                (0.0, Color("#FF0000")),
                (1.0, Color("#0000FF")),
            ]
        }

        element = VElement(keystates=states, property_keystates=property_keystates)

        result = benchmark(element.get_frame, 0.5)
        assert result is not None



@pytest.mark.benchmark
class TestColorPerformance:
    """Benchmark color operations"""

    def test_color_interpolation(self, benchmark):
        """Benchmark color interpolation"""
        color1 = Color("#FF0000")
        color2 = Color("#0000FF")

        result = benchmark(color1.interpolate, color2, 0.5)
        assert result is not None

    def test_color_creation_from_hex(self, benchmark):
        """Benchmark color creation from hex string"""
        result = benchmark(Color, "#FF8800")
        assert result is not None

    def test_color_creation_from_rgb(self, benchmark):
        """Benchmark color creation from RGB values"""
        result = benchmark(Color, 255, 128, 64)
        assert result is not None


@pytest.mark.benchmark
class TestPoint2DPerformance:
    """Benchmark Point2D operations"""

    def test_point2d_lerp(self, benchmark):
        """Benchmark Point2D linear interpolation"""
        p1 = Point2D(0, 0)
        p2 = Point2D(100, 100)

        result = benchmark(p1.lerp, p2, 0.5)
        assert result is not None

    def test_point2d_ilerp(self, benchmark):
        """Benchmark Point2D in-place interpolation"""
        p1 = Point2D(0, 0)
        p2 = Point2D(100, 100)

        def ilerp_operation():
            p = Point2D(0, 0)
            p.ilerp(p2, 0.5)
            return p

        result = benchmark(ilerp_operation)
        assert result is not None

    def test_point2d_distance(self, benchmark):
        """Benchmark Point2D distance calculation"""
        p1 = Point2D(0, 0)
        p2 = Point2D(100, 100)

        result = benchmark(p1.distance_to, p2)
        assert result is not None


@pytest.mark.benchmark
class TestFrameGenerationPerformance:
    """Benchmark frame generation for animations"""

    def test_generate_100_frames(self, benchmark):
        """Benchmark generating 100 frames"""
        states = [
            CircleState(x=0, y=0, radius=50, fill_color=Color("#FF0000")),
            CircleState(x=100, y=100, radius=100, fill_color=Color("#0000FF")),
        ]
        element = VElement(keystates=states)

        def generate_frames():
            frames = []
            for i in range(100):
                t = i / 99
                frames.append(element.get_frame(t))
            return frames

        result = benchmark(generate_frames)
        assert len(result) == 100

    def test_generate_1000_frames(self, benchmark):
        """Benchmark generating 1000 frames (typical 30fps, 33s video)"""
        states = [
            CircleState(x=0, y=0, radius=50),
            CircleState(x=100, y=100, radius=100),
        ]
        element = VElement(keystates=states)

        def generate_frames():
            frames = []
            for i in range(1000):
                t = i / 999
                frames.append(element.get_frame(t))
            return frames

        result = benchmark(generate_frames)
        assert len(result) == 1000


# Benchmark groups for easy filtering
# Run specific groups with: pytest -m "benchmark and interpolation"
pytestmark = pytest.mark.benchmark
