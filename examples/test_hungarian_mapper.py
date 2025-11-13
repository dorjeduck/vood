"""Test Hungarian matcher for optimal hole assignment"""

from vood.component.state.perforated_shape import PerforatedShapeState

# Check if scipy is available
try:
    from vood.transition.interpolation.hole_mapping import HungarianMapper
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("\n⚠️  scipy not installed - Hungarian matcher unavailable")
    print("    Install with: pip install scipy\n")


def test_hungarian_matcher():
    """Test Hungarian matcher for optimal assignment"""

    if not SCIPY_AVAILABLE:
        print("Skipping Hungarian matcher test (scipy not installed)")
        return

    # Create test states (5→2 merging)
    state1 = PerforatedShapeState(
        outer_shape={"type": "astroid", "radius": 120, "num_cusps": 8, "curvature": 0.65},
        holes=[
            {"type": "circle", "radius": 15, "x": 0, "y": 0},
            {"type": "astroid", "radius": 18, "num_cusps": 3, "curvature": 0.8, "x": -50, "y": 0},
            {"type": "astroid", "radius": 18, "num_cusps": 3, "curvature": 0.8, "x": 50, "y": 0},
            {"type": "square", "size": 20, "x": 0, "y": -50},
            {"type": "square", "size": 20, "x": 0, "y": 50},
        ],
    )

    state2 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 150},
        holes=[
            {"type": "astroid", "radius": 35, "num_cusps": 4, "curvature": 0.3, "x": -70, "y": -70},
            {"type": "astroid", "radius": 35, "num_cusps": 4, "curvature": 0.9, "x": 70, "y": 70},
        ],
    )

    # Generate contours
    contours1 = state1._generate_contours()
    contours2 = state2._generate_contours()

    print(f"\n5 holes → 2 holes Hungarian matching test")
    print(f"=" * 60)
    print(f"\nSource holes (5):")
    for i, hole in enumerate(contours1.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    print(f"\nDestination holes (2):")
    for i, hole in enumerate(contours2.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    # Test Hungarian matcher
    matcher = HungarianMapper()
    matched1, matched2 = matcher.match(contours1.holes, contours2.holes)

    # Count distribution
    dest_counts = {}
    total_distance = 0
    for src_hole, dest_hole in zip(matched1, matched2):
        src_c = src_hole.centroid()
        dest_c = dest_hole.centroid()
        dist = ((src_c[0] - dest_c[0])**2 + (src_c[1] - dest_c[1])**2)**0.5
        total_distance += dist

        key = f"({dest_c[0]:.1f}, {dest_c[1]:.1f})"
        dest_counts[key] = dest_counts.get(key, 0) + 1

    print(f"\n✓ Hungarian Matching Results:")
    for dest, count in sorted(dest_counts.items()):
        print(f"  {count} holes → destination at {dest}")

    counts = list(dest_counts.values())
    max_count = max(counts)
    min_count = min(counts)
    print(f"\n  Balance: {min_count}-{max_count} split (difference: {max_count - min_count})")
    print(f"  Total distance: {total_distance:.1f}")

    if max_count - min_count <= 1:
        print(f"  ✅ BALANCED: Clusters differ by at most 1 hole")
    else:
        print(f"  ⚠️  IMBALANCED: Difference of {max_count - min_count} holes")

    # Compare with other matchers
    print(f"\n" + "=" * 60)
    print("Comparison with other matchers:")
    print("=" * 60)

    # Greedy
    from vood.transition.interpolation.hole_mapping import GreedyNearestMapper
    greedy_matcher = GreedyNearestMapper()
    matched1_g, matched2_g = greedy_matcher.match(contours1.holes, contours2.holes)

    dest_counts_g = {}
    total_distance_g = 0
    for src_hole, dest_hole in zip(matched1_g, matched2_g):
        src_c = src_hole.centroid()
        dest_c = dest_hole.centroid()
        dist = ((src_c[0] - dest_c[0])**2 + (src_c[1] - dest_c[1])**2)**0.5
        total_distance_g += dist
        key = f"({dest_c[0]:.1f}, {dest_c[1]:.1f})"
        dest_counts_g[key] = dest_counts_g.get(key, 0) + 1

    counts_g = list(dest_counts_g.values())
    print(f"\nGreedy:           {min(counts_g)}-{max(counts_g)} split, distance: {total_distance_g:.1f}")

    # Clustering (balanced)
    from vood.transition.interpolation.hole_mapping import ClusteringMapper
    clustering_matcher = ClusteringMapper(balance_clusters=True)
    matched1_c, matched2_c = clustering_matcher.match(contours1.holes, contours2.holes)

    dest_counts_c = {}
    total_distance_c = 0
    for src_hole, dest_hole in zip(matched1_c, matched2_c):
        src_c = src_hole.centroid()
        dest_c = dest_hole.centroid()
        dist = ((src_c[0] - dest_c[0])**2 + (src_c[1] - dest_c[1])**2)**0.5
        total_distance_c += dist
        key = f"({dest_c[0]:.1f}, {dest_c[1]:.1f})"
        dest_counts_c[key] = dest_counts_c.get(key, 0) + 1

    counts_c = list(dest_counts_c.values())
    print(f"Clustering (bal): {min(counts_c)}-{max(counts_c)} split, distance: {total_distance_c:.1f}")
    print(f"Hungarian:        {min_count}-{max_count} split, distance: {total_distance:.1f}")

    print(f"\n{'✅ Hungarian has LOWEST total distance' if total_distance <= min(total_distance_g, total_distance_c) else '⚠️  Another matcher has lower distance'}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_hungarian_matcher()
