"""Test discrete hole matching strategy"""

from vood.component.state.perforated_shape import PerforatedShapeState
from vood.transition.interpolation.hole_mapping import DiscreteMapper


def test_discrete_merging():
    """Test 5→2 merging with discrete strategy"""

    print("\n" + "=" * 60)
    print("Test: 5 holes → 2 holes (MERGING with discrete strategy)")
    print("=" * 60)

    # Create states (5→2 merging)
    state1 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 15, "x": 0, "y": 0},      # center
            {"type": "circle", "radius": 15, "x": -50, "y": 0},    # left
            {"type": "circle", "radius": 15, "x": 50, "y": 0},     # right
            {"type": "circle", "radius": 15, "x": 0, "y": -50},    # top
            {"type": "circle", "radius": 15, "x": 0, "y": 50},     # bottom
        ],
    )

    state2 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 20, "x": -70, "y": -70},  # upper-left
            {"type": "circle", "radius": 20, "x": 70, "y": 70},    # lower-right
        ],
    )

    # Generate contours
    contours1 = state1._generate_contours()
    contours2 = state2._generate_contours()

    print("\nSource holes (5):")
    for i, hole in enumerate(contours1.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    print("\nDestination holes (2):")
    for i, hole in enumerate(contours2.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    # Test discrete matcher
    matcher = DiscreteMapper()
    matched1, matched2 = matcher.match(contours1.holes, contours2.holes)

    # Analyze results
    print("\n✓ Discrete Strategy Results:")

    moving = []
    disappearing = []

    for src, dst in zip(matched1, matched2):
        src_c = src.centroid()
        dst_c = dst.centroid()

        # Check if destination is zero-sized (disappearing)
        dst_radius = sum((v[0] - dst_c[0])**2 + (v[1] - dst_c[1])**2
                        for v in dst.vertices) / len(dst.vertices)

        if dst_radius < 0.1:  # Zero-sized hole
            disappearing.append(src_c)
            print(f"  Hole at ({src_c[0]:.1f}, {src_c[1]:.1f}) → DISAPPEARS in place")
        else:
            moving.append((src_c, dst_c))
            print(f"  Hole at ({src_c[0]:.1f}, {src_c[1]:.1f}) → moves to ({dst_c[0]:.1f}, {dst_c[1]:.1f})")

    print(f"\nSummary:")
    print(f"  {len(moving)} holes MOVE to destinations")
    print(f"  {len(disappearing)} holes DISAPPEAR in place")
    print(f"  Expected: 2 move, 3 disappear")

    if len(moving) == 2 and len(disappearing) == 3:
        print("  ✅ CORRECT!")
    else:
        print("  ⚠️  UNEXPECTED distribution")


def test_discrete_splitting():
    """Test 1→3 splitting with discrete strategy"""

    print("\n" + "=" * 60)
    print("Test: 1 hole → 3 holes (SPLITTING with discrete strategy)")
    print("=" * 60)

    # Create states (1→3 splitting)
    state1 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 20, "x": 0, "y": 0},      # center
        ],
    )

    state2 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 15, "x": -50, "y": 0},    # left
            {"type": "circle", "radius": 15, "x": 0, "y": 0},      # center
            {"type": "circle", "radius": 15, "x": 50, "y": 0},     # right
        ],
    )

    # Generate contours
    contours1 = state1._generate_contours()
    contours2 = state2._generate_contours()

    print("\nSource holes (1):")
    for i, hole in enumerate(contours1.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    print("\nDestination holes (3):")
    for i, hole in enumerate(contours2.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    # Test discrete matcher
    matcher = DiscreteMapper()
    matched1, matched2 = matcher.match(contours1.holes, contours2.holes)

    # Analyze results
    print("\n✓ Discrete Strategy Results:")

    moving = []
    appearing = []

    for src, dst in zip(matched1, matched2):
        src_c = src.centroid()
        dst_c = dst.centroid()

        # Check if source is zero-sized (appearing)
        src_radius = sum((v[0] - src_c[0])**2 + (v[1] - src_c[1])**2
                        for v in src.vertices) / len(src.vertices)

        if src_radius < 0.1:  # Zero-sized hole
            appearing.append(dst_c)
            print(f"  Hole APPEARS at ({dst_c[0]:.1f}, {dst_c[1]:.1f}) from nothing")
        else:
            moving.append((src_c, dst_c))
            print(f"  Hole at ({src_c[0]:.1f}, {src_c[1]:.1f}) → moves to ({dst_c[0]:.1f}, {dst_c[1]:.1f})")

    print(f"\nSummary:")
    print(f"  {len(moving)} hole MOVES to destination")
    print(f"  {len(appearing)} holes APPEAR from nothing")
    print(f"  Expected: 1 move, 2 appear")

    if len(moving) == 1 and len(appearing) == 2:
        print("  ✅ CORRECT!")
    else:
        print("  ⚠️  UNEXPECTED distribution")


def test_comparison_with_clustering():
    """Compare discrete vs clustering for same transition"""

    print("\n" + "=" * 60)
    print("Comparison: Discrete vs Clustering (5→2)")
    print("=" * 60)

    # Create states
    state1 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 15, "x": 0, "y": 0},
            {"type": "circle", "radius": 15, "x": -50, "y": 0},
            {"type": "circle", "radius": 15, "x": 50, "y": 0},
            {"type": "circle", "radius": 15, "x": 0, "y": -50},
            {"type": "circle", "radius": 15, "x": 0, "y": 50},
        ],
    )

    state2 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 20, "x": -70, "y": -70},
            {"type": "circle", "radius": 20, "x": 70, "y": 70},
        ],
    )

    contours1 = state1._generate_contours()
    contours2 = state2._generate_contours()

    # Test both matchers
    from vood.transition.interpolation.hole_mapping import ClusteringMapper

    discrete_matcher = DiscreteMapper()
    clustering_matcher = ClusteringMapper(balance_clusters=True)

    matched1_d, matched2_d = discrete_matcher.match(contours1.holes, contours2.holes)
    matched1_c, matched2_c = clustering_matcher.match(contours1.holes, contours2.holes)

    # Count behaviors
    def count_behaviors(matched1, matched2):
        moving = 0
        disappearing = 0
        for src, dst in zip(matched1, matched2):
            dst_c = dst.centroid()
            dst_radius = sum((v[0] - dst_c[0])**2 + (v[1] - dst_c[1])**2
                            for v in dst.vertices) / len(dst.vertices)
            if dst_radius < 0.1:
                disappearing += 1
            else:
                moving += 1
        return moving, disappearing

    discrete_moving, discrete_vanish = count_behaviors(matched1_d, matched2_d)
    clustering_moving, clustering_vanish = count_behaviors(matched1_c, matched2_c)

    print("\nDiscrete Strategy:")
    print(f"  {discrete_moving} holes move, {discrete_vanish} disappear")
    print(f"  Visual: Discrete, clean transitions")

    print("\nClustering (Balanced):")
    print(f"  {clustering_moving} holes move, {clustering_vanish} disappear")
    print(f"  Visual: All holes converge and merge")

    print("\nKey Difference:")
    print("  Discrete: Some holes shrink away, others move")
    print("  Clustering: All holes move toward merge points")
    print("=" * 60)


if __name__ == "__main__":
    test_discrete_merging()
    test_discrete_splitting()
    test_comparison_with_clustering()
    print("\n✅ All discrete strategy tests completed!\n")
