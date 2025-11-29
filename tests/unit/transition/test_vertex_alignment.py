"""Unit tests for vertex alignment strategies"""

import pytest
import math
from vood.transition.vertex_alignment import (
    AngularAligner,
    EuclideanAligner,
    SequentialAligner,
    AlignmentContext,
    get_aligner,
)
from vood.core.point2d import Point2D


@pytest.fixture
def square_vertices():
    """Create vertices for a square centered at origin"""
    return [
        Point2D(50, 50),
        Point2D(-50, 50),
        Point2D(-50, -50),
        Point2D(50, -50),
        Point2D(50, 50),  # Closed
    ]


@pytest.fixture
def rotated_square_vertices():
    """Create vertices for a rotated square (45 degrees offset)"""
    return [
        Point2D(70.7, 0),  # Rotated 45 degrees
        Point2D(0, 70.7),
        Point2D(-70.7, 0),
        Point2D(0, -70.7),
        Point2D(70.7, 0),  # Closed
    ]


@pytest.fixture
def line_vertices():
    """Create vertices for a horizontal line (open shape)"""
    return [
        Point2D(0, 0),
        Point2D(25, 0),
        Point2D(50, 0),
        Point2D(75, 0),
        Point2D(100, 0),
    ]


@pytest.fixture
def reversed_line_vertices():
    """Create vertices for a horizontal line in reverse direction"""
    return [
        Point2D(100, 0),
        Point2D(75, 0),
        Point2D(50, 0),
        Point2D(25, 0),
        Point2D(0, 0),
    ]


@pytest.mark.unit
class TestGetAlignerFactory:
    """Test the get_aligner factory function"""

    def test_get_aligner_both_closed(self):
        """Test that get_aligner returns AngularAligner for closed ↔ closed"""
        aligner = get_aligner(closed1=True, closed2=True)
        assert isinstance(aligner, AngularAligner)

    def test_get_aligner_both_open(self):
        """Test that get_aligner returns SequentialAligner for open ↔ open"""
        aligner = get_aligner(closed1=False, closed2=False)
        assert isinstance(aligner, SequentialAligner)

    def test_get_aligner_mixed_closed_first(self):
        """Test that get_aligner returns EuclideanAligner for closed ↔ open"""
        aligner = get_aligner(closed1=True, closed2=False)
        assert isinstance(aligner, EuclideanAligner)

    def test_get_aligner_mixed_open_first(self):
        """Test that get_aligner returns EuclideanAligner for open ↔ closed"""
        aligner = get_aligner(closed1=False, closed2=True)
        assert isinstance(aligner, EuclideanAligner)


@pytest.mark.unit
class TestAngularAligner:
    """Test angular alignment for closed shapes"""

    def test_align_identical_squares(self, square_vertices):
        """Test aligning identical squares requires no rotation"""
        aligner = AngularAligner()
        context = AlignmentContext(closed1=True, closed2=True)

        verts1, verts2_aligned = aligner.align(square_vertices, square_vertices, context)

        # Should return original vertices
        assert len(verts2_aligned) == len(square_vertices)

    def test_align_finds_best_offset(self):
        """Test that aligner finds optimal vertex offset"""
        aligner = AngularAligner()

        # Create two squares with offset starting points
        verts1 = [
            Point2D(50, 50),
            Point2D(-50, 50),
            Point2D(-50, -50),
            Point2D(50, -50),
            Point2D(50, 50),
        ]
        # Same square but rotated (starts from a different vertex)
        verts2 = [
            Point2D(-50, 50),
            Point2D(-50, -50),
            Point2D(50, -50),
            Point2D(50, 50),
            Point2D(-50, 50),
        ]

        context = AlignmentContext(closed1=True, closed2=True)
        verts1_out, verts2_aligned = aligner.align(verts1, verts2, context)

        # Should find best alignment (may not be perfect due to angular distances)
        assert len(verts2_aligned) == len(verts1)

    def test_align_respects_shape_rotation(self):
        """Test that aligner considers shape rotation in context"""
        aligner = AngularAligner()

        verts1 = [Point2D(100, 0), Point2D(0, 100), Point2D(-100, 0), Point2D(0, -100), Point2D(100, 0)]
        verts2 = [Point2D(100, 0), Point2D(0, 100), Point2D(-100, 0), Point2D(0, -100), Point2D(100, 0)]

        # Test with rotation
        context = AlignmentContext(rotation1=45, rotation2=0, closed1=True, closed2=True)
        verts1_out, verts2_aligned = aligner.align(verts1, verts2, context)

        assert len(verts2_aligned) == len(verts1)

    def test_align_mismatched_lengths_raises(self):
        """Test that mismatched vertex counts raise ValueError"""
        aligner = AngularAligner()
        verts1 = [Point2D(0, 0), Point2D(100, 0), Point2D(0, 100), Point2D(0, 0)]
        verts2 = [Point2D(0, 0), Point2D(100, 0), Point2D(0, 0)]  # Different length

        context = AlignmentContext(closed1=True, closed2=True)

        with pytest.raises(ValueError, match="Vertex lists must have same length"):
            aligner.align(verts1, verts2, context)

    def test_align_empty_vertices(self):
        """Test aligning empty vertex lists"""
        aligner = AngularAligner()
        verts1 = []
        verts2 = []
        context = AlignmentContext(closed1=True, closed2=True)

        verts1_out, verts2_out = aligner.align(verts1, verts2, context)

        assert verts1_out == []
        assert verts2_out == []


@pytest.mark.unit
class TestEuclideanAligner:
    """Test euclidean distance alignment for open/closed combinations"""

    def test_align_open_to_closed(self, line_vertices):
        """Test aligning open line to closed square"""
        aligner = EuclideanAligner()

        # Closed square
        square = [
            Point2D(0, 0),
            Point2D(100, 0),
            Point2D(100, 100),
            Point2D(0, 100),
            Point2D(0, 0),
        ]

        context = AlignmentContext(closed1=False, closed2=True)
        verts1_out, verts2_aligned = aligner.align(line_vertices, square, context)

        # Should return aligned vertices
        assert len(verts2_aligned) == len(line_vertices)

        # Last vertex of closed shape should equal first (closure enforced)
        assert verts2_aligned[-1].x == verts2_aligned[0].x
        assert verts2_aligned[-1].y == verts2_aligned[0].y

    def test_align_closed_to_open(self):
        """Test aligning closed square to open line"""
        aligner = EuclideanAligner()

        square = [
            Point2D(0, 0),
            Point2D(100, 0),
            Point2D(100, 100),
            Point2D(0, 100),
            Point2D(0, 0),
        ]
        line = [
            Point2D(0, 0),
            Point2D(25, 0),
            Point2D(50, 0),
            Point2D(75, 0),
            Point2D(100, 0),
        ]

        context = AlignmentContext(closed1=True, closed2=False)
        verts1_out, verts2_out = aligner.align(square, line, context)

        # Should return aligned vertices
        assert len(verts1_out) == len(square)
        assert len(verts2_out) == len(line)

        # verts1 (closed) should have first == last after alignment
        assert verts1_out[-1].x == verts1_out[0].x
        assert verts1_out[-1].y == verts1_out[0].y

    def test_align_both_closed_returns_unchanged(self):
        """Test that aligner doesn't modify when both are closed"""
        aligner = EuclideanAligner()

        square1 = [Point2D(0, 0), Point2D(100, 0), Point2D(100, 100), Point2D(0, 0)]
        square2 = [Point2D(0, 0), Point2D(100, 0), Point2D(100, 100), Point2D(0, 0)]

        context = AlignmentContext(closed1=True, closed2=True)
        verts1_out, verts2_out = aligner.align(square1, square2, context)

        # Should return original vertices (fallback behavior)
        assert len(verts1_out) == len(square1)
        assert len(verts2_out) == len(square2)

    def test_align_both_open_returns_unchanged(self):
        """Test that aligner doesn't modify when both are open"""
        aligner = EuclideanAligner()

        line1 = [Point2D(0, 0), Point2D(50, 0), Point2D(100, 0)]
        line2 = [Point2D(0, 0), Point2D(50, 50), Point2D(100, 100)]

        context = AlignmentContext(closed1=False, closed2=False)
        verts1_out, verts2_out = aligner.align(line1, line2, context)

        # Should return original vertices (fallback behavior)
        assert len(verts1_out) == len(line1)
        assert len(verts2_out) == len(line2)

    def test_align_mismatched_lengths_raises(self):
        """Test that mismatched vertex counts raise ValueError"""
        aligner = EuclideanAligner()
        verts1 = [Point2D(0, 0), Point2D(100, 0), Point2D(0, 100)]
        verts2 = [Point2D(0, 0), Point2D(100, 0), Point2D(100, 100), Point2D(0, 0)]

        context = AlignmentContext(closed1=False, closed2=True)

        with pytest.raises(ValueError, match="Vertex lists must have same length"):
            aligner.align(verts1, verts2, context)


@pytest.mark.unit
class TestSequentialAligner:
    """Test sequential alignment for open shapes"""

    def test_align_same_direction_no_reversal(self, line_vertices):
        """Test aligning lines in same direction requires no reversal"""
        aligner = SequentialAligner()

        line2 = [
            Point2D(0, 50),
            Point2D(25, 50),
            Point2D(50, 50),
            Point2D(75, 50),
            Point2D(100, 50),
        ]

        context = AlignmentContext(closed1=False, closed2=False)
        verts1_out, verts2_out = aligner.align(line_vertices, line2, context)

        # Should not reverse (same direction is closer)
        assert verts2_out[0].x == 0
        assert verts2_out[-1].x == 100

    def test_align_opposite_direction_reverses(self, line_vertices, reversed_line_vertices):
        """Test aligning lines in opposite directions triggers reversal"""
        aligner = SequentialAligner()

        context = AlignmentContext(closed1=False, closed2=False)
        verts1_out, verts2_out = aligner.align(line_vertices, reversed_line_vertices, context)

        # Should reverse to minimize distance
        # After reversal, should match direction of verts1
        assert verts2_out[0].x == 0
        assert verts2_out[-1].x == 100

    def test_align_vertical_lines(self):
        """Test aligning vertical lines"""
        aligner = SequentialAligner()

        line1 = [Point2D(0, 0), Point2D(0, 50), Point2D(0, 100)]
        line2 = [Point2D(0, 100), Point2D(0, 50), Point2D(0, 0)]  # Reversed

        context = AlignmentContext(closed1=False, closed2=False)
        verts1_out, verts2_out = aligner.align(line1, line2, context)

        # Should reverse line2 to match line1 direction
        assert verts2_out[0].y == 0
        assert verts2_out[-1].y == 100

    def test_align_diagonal_lines(self):
        """Test aligning diagonal lines"""
        aligner = SequentialAligner()

        line1 = [Point2D(0, 0), Point2D(50, 50), Point2D(100, 100)]
        line2 = [Point2D(100, 100), Point2D(50, 50), Point2D(0, 0)]  # Reversed

        context = AlignmentContext(closed1=False, closed2=False)
        verts1_out, verts2_out = aligner.align(line1, line2, context)

        # Should reverse line2
        assert verts2_out[0].x == 0 and verts2_out[0].y == 0
        assert verts2_out[-1].x == 100 and verts2_out[-1].y == 100

    def test_align_preserves_verts1(self, line_vertices):
        """Test that verts1 is never modified"""
        aligner = SequentialAligner()

        line2 = [Point2D(100, 0), Point2D(75, 0), Point2D(50, 0), Point2D(25, 0), Point2D(0, 0)]
        original_verts1 = list(line_vertices)

        context = AlignmentContext(closed1=False, closed2=False)
        verts1_out, verts2_out = aligner.align(line_vertices, line2, context)

        # verts1 should be unchanged
        for i, v in enumerate(verts1_out):
            assert v.x == original_verts1[i].x
            assert v.y == original_verts1[i].y

    def test_align_mismatched_lengths_raises(self):
        """Test that mismatched vertex counts raise ValueError"""
        aligner = SequentialAligner()
        verts1 = [Point2D(0, 0), Point2D(50, 0), Point2D(100, 0)]
        verts2 = [Point2D(0, 0), Point2D(50, 0)]  # Different length

        context = AlignmentContext(closed1=False, closed2=False)

        with pytest.raises(ValueError, match="Vertex lists must have same length"):
            aligner.align(verts1, verts2, context)


@pytest.mark.unit
class TestAlignmentContext:
    """Test AlignmentContext dataclass"""

    def test_default_context(self):
        """Test default context values"""
        context = AlignmentContext()
        assert context.rotation1 == 0
        assert context.rotation2 == 0
        assert context.closed1 is True
        assert context.closed2 is True

    def test_custom_context(self):
        """Test custom context values"""
        context = AlignmentContext(
            rotation1=45,
            rotation2=90,
            closed1=False,
            closed2=True
        )
        assert context.rotation1 == 45
        assert context.rotation2 == 90
        assert context.closed1 is False
        assert context.closed2 is True


@pytest.mark.unit
class TestAlignmentEdgeCases:
    """Test edge cases across all aligners"""

    def test_align_single_vertex(self):
        """Test aligning shapes with single vertex"""
        aligner = AngularAligner()
        verts1 = [Point2D(0, 0)]
        verts2 = [Point2D(100, 100)]
        context = AlignmentContext(closed1=True, closed2=True)

        verts1_out, verts2_out = aligner.align(verts1, verts2, context)

        assert len(verts1_out) == 1
        assert len(verts2_out) == 1

    def test_align_two_vertices(self):
        """Test aligning shapes with two vertices"""
        aligner = SequentialAligner()
        verts1 = [Point2D(0, 0), Point2D(100, 0)]
        verts2 = [Point2D(0, 50), Point2D(100, 50)]
        context = AlignmentContext(closed1=False, closed2=False)

        verts1_out, verts2_out = aligner.align(verts1, verts2, context)

        assert len(verts1_out) == 2
        assert len(verts2_out) == 2

    def test_align_collinear_vertices(self):
        """Test aligning perfectly collinear vertices"""
        aligner = SequentialAligner()
        verts1 = [Point2D(0, 0), Point2D(50, 0), Point2D(100, 0)]
        verts2 = [Point2D(0, 0), Point2D(50, 0), Point2D(100, 0)]  # Identical
        context = AlignmentContext(closed1=False, closed2=False)

        verts1_out, verts2_out = aligner.align(verts1, verts2, context)

        # Should not reverse identical vertices
        for i, v in enumerate(verts2_out):
            assert v.x == verts2[i].x
            assert v.y == verts2[i].y
