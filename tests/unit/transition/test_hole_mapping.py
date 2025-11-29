"""Unit tests for hole mapping strategies"""

import pytest
from vood.transition.hole_mapping import (
    GreedyNearestMapper,
    create_zero_hole,
)
from vood.component.vertex.vertex_loop import VertexLoop
from vood.core.point2d import Point2D


@pytest.fixture
def hole_at_origin():
    """Create a small square hole at origin"""
    vertices = [
        Point2D(0, 0),
        Point2D(10, 0),
        Point2D(10, 10),
        Point2D(0, 10),
        Point2D(0, 0),
    ]
    return VertexLoop(vertices, closed=True)


@pytest.fixture
def hole_at_50_50():
    """Create a small square hole at (50, 50)"""
    vertices = [
        Point2D(50, 50),
        Point2D(60, 50),
        Point2D(60, 60),
        Point2D(50, 60),
        Point2D(50, 50),
    ]
    return VertexLoop(vertices, closed=True)


@pytest.fixture
def hole_at_100_100():
    """Create a small square hole at (100, 100)"""
    vertices = [
        Point2D(100, 100),
        Point2D(110, 100),
        Point2D(110, 110),
        Point2D(100, 110),
        Point2D(100, 100),
    ]
    return VertexLoop(vertices, closed=True)


@pytest.fixture
def hole_at_150_150():
    """Create a small square hole at (150, 150)"""
    vertices = [
        Point2D(150, 150),
        Point2D(160, 150),
        Point2D(160, 160),
        Point2D(150, 160),
        Point2D(150, 150),
    ]
    return VertexLoop(vertices, closed=True)


@pytest.mark.unit
class TestZeroHoleCreation:
    """Test zero-sized hole creation utility"""

    def test_create_zero_hole_at_centroid(self, hole_at_origin):
        """Test that zero hole is created at centroid"""
        zero = create_zero_hole(hole_at_origin)

        # All vertices should be at centroid (5, 5)
        centroid = hole_at_origin.centroid()
        for vertex in zero.vertices:
            assert vertex.x == centroid.x
            assert vertex.y == centroid.y

    def test_create_zero_hole_preserves_count(self, hole_at_origin):
        """Test that zero hole has same vertex count as reference"""
        zero = create_zero_hole(hole_at_origin)
        assert len(zero.vertices) == len(hole_at_origin.vertices)

    def test_create_zero_hole_is_closed(self, hole_at_origin):
        """Test that zero hole is marked as closed"""
        zero = create_zero_hole(hole_at_origin)
        assert zero.closed is True


@pytest.mark.unit
class TestGreedyMapperEqualCounts:
    """Test greedy mapper with N=M (equal hole counts)"""

    def test_map_single_hole_to_single_hole(self, hole_at_origin, hole_at_100_100):
        """Test mapping 1 hole to 1 hole"""
        mapper = GreedyNearestMapper()
        holes1 = [hole_at_origin]
        holes2 = [hole_at_100_100]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        assert len(mapped1) == 1
        assert len(mapped2) == 1
        assert mapped1[0] is hole_at_origin
        assert mapped2[0] is hole_at_100_100

    def test_map_two_holes_to_two_holes(
        self, hole_at_origin, hole_at_50_50, hole_at_100_100, hole_at_150_150
    ):
        """Test mapping 2 holes to 2 holes by nearest centroids"""
        mapper = GreedyNearestMapper()

        # holes1: at (0,0) and (100,100)
        # holes2: at (50,50) and (150,150)
        # Expected: (0,0) -> (50,50), (100,100) -> (150,150)
        holes1 = [hole_at_origin, hole_at_100_100]
        holes2 = [hole_at_50_50, hole_at_150_150]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        assert len(mapped1) == 2
        assert len(mapped2) == 2

        # Check that nearest pairs are matched
        # hole_at_origin (0,0) should map to hole_at_50_50 (50,50)
        # hole_at_100_100 (100,100) should map to hole_at_150_150 (150,150)
        assert mapped1[0] is hole_at_origin
        assert mapped2[0] is hole_at_50_50
        assert mapped1[1] is hole_at_100_100
        assert mapped2[1] is hole_at_150_150

    def test_map_preserves_uniqueness_with_equal_counts(
        self, hole_at_origin, hole_at_50_50, hole_at_100_100, hole_at_150_150
    ):
        """Test that each hole is used exactly once with equal counts"""
        mapper = GreedyNearestMapper()
        holes1 = [hole_at_origin, hole_at_100_100]
        holes2 = [hole_at_50_50, hole_at_150_150]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        # Each hole should appear exactly once
        assert len(set(id(h) for h in mapped1)) == len(mapped1)
        assert len(set(id(h) for h in mapped2)) == len(mapped2)


@pytest.mark.unit
class TestGreedyMapperMoreSources:
    """Test greedy mapper with N>M (more source holes - merging)"""

    def test_map_two_holes_to_one(
        self, hole_at_origin, hole_at_50_50, hole_at_100_100
    ):
        """Test mapping 2 holes to 1 hole (merging)"""
        mapper = GreedyNearestMapper()

        # Two source holes, one dest hole
        # Both should map to the single dest
        holes1 = [hole_at_origin, hole_at_50_50]
        holes2 = [hole_at_100_100]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        assert len(mapped1) == 2
        assert len(mapped2) == 2

        # Both should map to the same dest hole
        assert mapped1[0] is hole_at_origin
        assert mapped1[1] is hole_at_50_50
        assert mapped2[0] is hole_at_100_100
        assert mapped2[1] is hole_at_100_100  # Reused

    def test_map_three_holes_to_two(
        self, hole_at_origin, hole_at_50_50, hole_at_100_100, hole_at_150_150
    ):
        """Test mapping 3 holes to 2 holes (some merging)"""
        mapper = GreedyNearestMapper()

        holes1 = [hole_at_origin, hole_at_50_50, hole_at_100_100]
        holes2 = [hole_at_origin, hole_at_150_150]  # At 0 and 150

        mapped1, mapped2 = mapper.map(holes1, holes2)

        assert len(mapped1) == 3
        assert len(mapped2) == 3

        # At least one dest hole should be used multiple times
        dest_ids = [id(h) for h in mapped2]
        assert len(set(dest_ids)) < len(dest_ids)


@pytest.mark.unit
class TestGreedyMapperFewerSources:
    """Test greedy mapper with N<M (fewer source holes - splitting)"""

    def test_map_one_hole_to_two(
        self, hole_at_origin, hole_at_50_50, hole_at_100_100
    ):
        """Test mapping 1 hole to 2 holes (splitting)"""
        mapper = GreedyNearestMapper()

        # One source hole, two dest holes
        # Source should be duplicated
        holes1 = [hole_at_50_50]
        holes2 = [hole_at_origin, hole_at_100_100]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        assert len(mapped1) == 2
        assert len(mapped2) == 2

        # Same source hole should be used for both mappings
        assert mapped1[0] is hole_at_50_50
        assert mapped1[1] is hole_at_50_50  # Reused

        # Both dest holes should be present
        assert mapped2[0] is hole_at_origin
        assert mapped2[1] is hole_at_100_100

    def test_map_two_holes_to_three(
        self, hole_at_origin, hole_at_50_50, hole_at_100_100, hole_at_150_150
    ):
        """Test mapping 2 holes to 3 holes (some splitting)"""
        mapper = GreedyNearestMapper()

        holes1 = [hole_at_origin, hole_at_150_150]
        holes2 = [hole_at_origin, hole_at_50_50, hole_at_150_150]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        assert len(mapped1) == 3
        assert len(mapped2) == 3

        # At least one source hole should be used multiple times
        source_ids = [id(h) for h in mapped1]
        assert len(set(source_ids)) < len(source_ids)


@pytest.mark.unit
class TestGreedyMapperZeroHoles:
    """Test greedy mapper with N=0 or M=0 (creation/destruction)"""

    def test_map_zero_to_zero(self):
        """Test mapping 0 holes to 0 holes"""
        mapper = GreedyNearestMapper()
        holes1 = []
        holes2 = []

        mapped1, mapped2 = mapper.map(holes1, holes2)

        assert len(mapped1) == 0
        assert len(mapped2) == 0

    def test_map_holes_to_zero(self, hole_at_origin, hole_at_50_50):
        """Test mapping N holes to 0 holes (holes disappear)"""
        mapper = GreedyNearestMapper()

        holes1 = [hole_at_origin, hole_at_50_50]
        holes2 = []

        mapped1, mapped2 = mapper.map(holes1, holes2)

        # Should have same number of mappings as source holes
        assert len(mapped1) == 2
        assert len(mapped2) == 2

        # Source holes should be preserved
        assert mapped1[0] is hole_at_origin
        assert mapped1[1] is hole_at_50_50

        # Dest should be zero-sized holes at source centroids
        for i, source_hole in enumerate(holes1):
            centroid = source_hole.centroid()
            zero_hole = mapped2[i]

            # All vertices should be at centroid
            for vertex in zero_hole.vertices:
                assert vertex.x == centroid.x
                assert vertex.y == centroid.y

    def test_map_zero_to_holes(self, hole_at_origin, hole_at_50_50):
        """Test mapping 0 holes to M holes (holes appear)"""
        mapper = GreedyNearestMapper()

        holes1 = []
        holes2 = [hole_at_origin, hole_at_50_50]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        # Should have same number of mappings as dest holes
        assert len(mapped1) == 2
        assert len(mapped2) == 2

        # Dest holes should be preserved
        assert mapped2[0] is hole_at_origin
        assert mapped2[1] is hole_at_50_50

        # Source should be zero-sized holes at dest centroids
        for i, dest_hole in enumerate(holes2):
            centroid = dest_hole.centroid()
            zero_hole = mapped1[i]

            # All vertices should be at centroid
            for vertex in zero_hole.vertices:
                assert vertex.x == centroid.x
                assert vertex.y == centroid.y


@pytest.mark.unit
class TestGreedyMapperEdgeCases:
    """Test edge cases in hole mapping"""

    def test_map_overlapping_holes(self):
        """Test mapping holes that overlap spatially"""
        mapper = GreedyNearestMapper()

        # Create two holes at the same position
        hole1a = VertexLoop(
            [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10), Point2D(0, 0)],
            closed=True
        )
        hole1b = VertexLoop(
            [Point2D(5, 5), Point2D(15, 5), Point2D(15, 15), Point2D(5, 15), Point2D(5, 5)],
            closed=True
        )

        hole2a = VertexLoop(
            [Point2D(2, 2), Point2D(12, 2), Point2D(12, 12), Point2D(2, 12), Point2D(2, 2)],
            closed=True
        )
        hole2b = VertexLoop(
            [Point2D(7, 7), Point2D(17, 7), Point2D(17, 17), Point2D(7, 17), Point2D(7, 7)],
            closed=True
        )

        holes1 = [hole1a, hole1b]
        holes2 = [hole2a, hole2b]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        # Should still produce valid mapping
        assert len(mapped1) == 2
        assert len(mapped2) == 2

    def test_map_very_distant_holes(self):
        """Test mapping holes that are very far apart"""
        mapper = GreedyNearestMapper()

        hole1 = VertexLoop(
            [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10), Point2D(0, 0)],
            closed=True
        )
        hole2 = VertexLoop(
            [Point2D(10000, 10000), Point2D(10010, 10000),
             Point2D(10010, 10010), Point2D(10000, 10010), Point2D(10000, 10000)],
            closed=True
        )

        holes1 = [hole1]
        holes2 = [hole2]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        # Should still map correctly despite distance
        assert len(mapped1) == 1
        assert len(mapped2) == 1
        assert mapped1[0] is hole1
        assert mapped2[0] is hole2

    def test_map_with_different_vertex_counts(self):
        """Test mapping holes with different vertex counts"""
        mapper = GreedyNearestMapper()

        # Triangle hole
        hole1 = VertexLoop(
            [Point2D(0, 0), Point2D(10, 0), Point2D(5, 10), Point2D(0, 0)],
            closed=True
        )
        # Square hole
        hole2 = VertexLoop(
            [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10), Point2D(0, 0)],
            closed=True
        )

        holes1 = [hole1]
        holes2 = [hole2]

        mapped1, mapped2 = mapper.map(holes1, holes2)

        # Should map successfully
        assert len(mapped1) == 1
        assert len(mapped2) == 1
        # Note: Different vertex counts will be handled during interpolation
