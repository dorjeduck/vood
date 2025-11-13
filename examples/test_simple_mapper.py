"""Test simple hole matching strategy"""

from vood.component.state.perforated_shape import PerforatedShapeState
from vood.transition.interpolation.hole_mapping import SimpleMapper


def test_simple_merging():
    """Test 5→2 transition with simple strategy (all disappear/appear)"""

    print("\n" + "=" * 60)
    print("Test: 5 holes → 2 holes (SIMPLE strategy - all disappear/appear)")
    print("=" * 60)

    # Create states (5→2 transition)
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

    # Test simple matcher
    matcher = SimpleMapper()
    matched1, matched2 = matcher.match(contours1.holes, contours2.holes)

    # Analyze results
    print("\n✓ Simple Strategy Results:")
    print(f"  Total matched pairs: {len(matched1)}")

    old_disappearing = 0
    new_appearing = 0

    for src, dst in zip(matched1, matched2):
        src_c = src.centroid()
        dst_c = dst.centroid()

        # Check if source is zero-sized (new hole appearing)
        src_radius = sum((v[0] - src_c[0])**2 + (v[1] - src_c[1])**2
                        for v in src.vertices) / len(src.vertices)

        # Check if destination is zero-sized (old hole disappearing)
        dst_radius = sum((v[0] - dst_c[0])**2 + (v[1] - dst_c[1])**2
                        for v in dst.vertices) / len(dst.vertices)

        if src_radius < 0.1:  # New hole appearing
            new_appearing += 1
            print(f"  NEW hole APPEARS at ({dst_c[0]:.1f}, {dst_c[1]:.1f})")
        elif dst_radius < 0.1:  # Old hole disappearing
            old_disappearing += 1
            print(f"  OLD hole at ({src_c[0]:.1f}, {src_c[1]:.1f}) DISAPPEARS")
        else:
            # This shouldn't happen with SimpleMapper
            print(f"  ⚠️  UNEXPECTED: Hole moves from ({src_c[0]:.1f}, {src_c[1]:.1f}) to ({dst_c[0]:.1f}, {dst_c[1]:.1f})")

    print(f"\nSummary:")
    print(f"  {old_disappearing} OLD holes disappear")
    print(f"  {new_appearing} NEW holes appear")
    print(f"  Expected: 5 disappear, 2 appear")

    if old_disappearing == 5 and new_appearing == 2:
        print("  ✅ CORRECT!")
    else:
        print("  ⚠️  UNEXPECTED distribution")


def test_simple_splitting():
    """Test 1→3 transition with simple strategy"""

    print("\n" + "=" * 60)
    print("Test: 1 hole → 3 holes (SIMPLE strategy - all disappear/appear)")
    print("=" * 60)

    # Create states (1→3 transition)
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

    # Test simple matcher
    matcher = SimpleMapper()
    matched1, matched2 = matcher.match(contours1.holes, contours2.holes)

    # Analyze results
    print("\n✓ Simple Strategy Results:")

    old_disappearing = 0
    new_appearing = 0

    for src, dst in zip(matched1, matched2):
        src_c = src.centroid()
        dst_c = dst.centroid()

        # Check if source is zero-sized (new hole appearing)
        src_radius = sum((v[0] - src_c[0])**2 + (v[1] - src_c[1])**2
                        for v in src.vertices) / len(src.vertices)

        # Check if destination is zero-sized (old hole disappearing)
        dst_radius = sum((v[0] - dst_c[0])**2 + (v[1] - dst_c[1])**2
                        for v in dst.vertices) / len(dst.vertices)

        if src_radius < 0.1:  # New hole appearing
            new_appearing += 1
            print(f"  NEW hole APPEARS at ({dst_c[0]:.1f}, {dst_c[1]:.1f})")
        elif dst_radius < 0.1:  # Old hole disappearing
            old_disappearing += 1
            print(f"  OLD hole at ({src_c[0]:.1f}, {src_c[1]:.1f}) DISAPPEARS")

    print(f"\nSummary:")
    print(f"  {old_disappearing} OLD hole disappears")
    print(f"  {new_appearing} NEW holes appear")
    print(f"  Expected: 1 disappear, 3 appear")

    if old_disappearing == 1 and new_appearing == 3:
        print("  ✅ CORRECT!")
    else:
        print("  ⚠️  UNEXPECTED distribution")


def test_comparison_strategies():
    """Compare simple vs discrete vs clustering for same transition"""

    print("\n" + "=" * 60)
    print("Comparison: Simple vs Discrete vs Clustering (5→2)")
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

    # Test all three matchers
    from vood.transition.interpolation.hole_mapping import ClusteringMapper, DiscreteMapper

    simple_matcher = SimpleMapper()
    discrete_matcher = DiscreteMapper()
    clustering_matcher = ClusteringMapper(balance_clusters=True)

    matched1_s, matched2_s = simple_matcher.match(contours1.holes, contours2.holes)
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

    simple_moving, simple_vanish = count_behaviors(matched1_s, matched2_s)
    discrete_moving, discrete_vanish = count_behaviors(matched1_d, matched2_d)
    clustering_moving, clustering_vanish = count_behaviors(matched1_c, matched2_c)

    print("\nSimple Strategy:")
    print(f"  {simple_moving} holes move, {simple_vanish} disappear")
    print(f"  Visual: All old disappear, all new appear (complete independence)")

    print("\nDiscrete Strategy:")
    print(f"  {discrete_moving} holes move, {discrete_vanish} disappear")
    print(f"  Visual: Some holes move, others disappear (selective matching)")

    print("\nClustering (Balanced):")
    print(f"  {clustering_moving} holes move, {clustering_vanish} disappear")
    print(f"  Visual: All holes move and merge (fluid transitions)")

    print("\nKey Differences:")
    print("  Simple:     No matching - all old exit, all new enter")
    print("  Discrete:   Selective matching - closest holes move")
    print("  Clustering: Full merging - all holes converge spatially")
    print("=" * 60)


if __name__ == "__main__":
    test_simple_merging()
    test_simple_splitting()
    test_comparison_strategies()
    print("\n✅ All simple strategy tests completed!\n")
