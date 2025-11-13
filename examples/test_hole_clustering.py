"""Test to verify hole clustering balance"""

from vood.component.state.perforated_shape import PerforatedShapeState
from vood.transition.interpolation.hole_mapping import ClusteringMapper


def test_clustering_balance():
    """Test that 5→2 hole clustering produces balanced groups"""

    # Create states matching y.py example
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

    print(f"\n5 holes → 2 holes clustering test")
    print(f"=" * 50)
    print(f"\nSource holes (5):")
    for i, hole in enumerate(contours1.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    print(f"\nDestination holes (2):")
    for i, hole in enumerate(contours2.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    # Test with balanced clustering
    matcher = ClusteringMapper(balance_clusters=True)
    matched1, matched2 = matcher.match(contours1.holes, contours2.holes)

    # Count how many source holes go to each destination
    dest_counts = {}
    for i, dest_hole in enumerate(matched2):
        dest_centroid = dest_hole.centroid()
        key = f"({dest_centroid[0]:.1f}, {dest_centroid[1]:.1f})"
        dest_counts[key] = dest_counts.get(key, 0) + 1

    print(f"\n✓ Balanced Clustering Results:")
    for dest, count in sorted(dest_counts.items()):
        print(f"  {count} holes → destination at {dest}")

    # Verify balance
    counts = list(dest_counts.values())
    max_count = max(counts)
    min_count = min(counts)
    print(f"\n  Balance: {min_count}-{max_count} split (difference: {max_count - min_count})")

    if max_count - min_count <= 1:
        print(f"  ✅ BALANCED: Clusters differ by at most 1 hole")
    else:
        print(f"  ⚠️  IMBALANCED: Difference of {max_count - min_count} holes")

    # Compare with unbalanced clustering
    print(f"\n" + "=" * 50)
    matcher_unbalanced = ClusteringMapper(balance_clusters=False)
    matched1_unbal, matched2_unbal = matcher_unbalanced.match(contours1.holes, contours2.holes)

    dest_counts_unbal = {}
    for dest_hole in matched2_unbal:
        dest_centroid = dest_hole.centroid()
        key = f"({dest_centroid[0]:.1f}, {dest_centroid[1]:.1f})"
        dest_counts_unbal[key] = dest_counts_unbal.get(key, 0) + 1

    print(f"\n✗ Unbalanced Clustering Results (for comparison):")
    for dest, count in sorted(dest_counts_unbal.items()):
        print(f"  {count} holes → destination at {dest}")

    counts_unbal = list(dest_counts_unbal.values())
    max_count_unbal = max(counts_unbal)
    min_count_unbal = min(counts_unbal)
    print(f"\n  Balance: {min_count_unbal}-{max_count_unbal} split (difference: {max_count_unbal - min_count_unbal})")

    print(f"\n" + "=" * 50)
    print(f"\nConclusion: Balancing {'improved' if (max_count - min_count) < (max_count_unbal - min_count_unbal) else 'did not change'} the split")
    print()


if __name__ == "__main__":
    test_clustering_balance()
