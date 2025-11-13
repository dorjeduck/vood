"""Test hole splitting (2→5) balance"""

from vood.component.state.perforated_shape import PerforatedShapeState
from vood.transition.interpolation.hole_mapping import ClusteringMapper


def test_splitting_balance():
    """Test that 2→5 hole splitting produces balanced groups"""

    # Create states - REVERSED order (splitting instead of merging)
    state1 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 150},
        holes=[
            {"type": "astroid", "radius": 35, "num_cusps": 4, "curvature": 0.3, "x": -70, "y": -70},
            {"type": "astroid", "radius": 35, "num_cusps": 4, "curvature": 0.9, "x": 70, "y": 70},
        ],
    )

    state2 = PerforatedShapeState(
        outer_shape={"type": "astroid", "radius": 120, "num_cusps": 8, "curvature": 0.65},
        holes=[
            {"type": "circle", "radius": 15, "x": 0, "y": 0},
            {"type": "astroid", "radius": 18, "num_cusps": 3, "curvature": 0.8, "x": -50, "y": 0},
            {"type": "astroid", "radius": 18, "num_cusps": 3, "curvature": 0.8, "x": 50, "y": 0},
            {"type": "square", "size": 20, "x": 0, "y": -50},
            {"type": "square", "size": 20, "x": 0, "y": 50},
        ],
    )

    # Generate contours
    contours1 = state1._generate_contours()
    contours2 = state2._generate_contours()

    print(f"\n2 holes → 5 holes splitting test")
    print(f"=" * 50)
    print(f"\nSource holes (2):")
    for i, hole in enumerate(contours1.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    print(f"\nDestination holes (5):")
    for i, hole in enumerate(contours2.holes):
        cx, cy = hole.centroid()
        print(f"  Hole {i}: ({cx:.1f}, {cy:.1f})")

    # Test with balanced clustering
    matcher = ClusteringMapper(balance_clusters=True)
    matched1, matched2 = matcher.match(contours1.holes, contours2.holes)

    # Count how many destinations each source splits into
    source_counts = {}
    for i, source_hole in enumerate(matched1):
        source_centroid = source_hole.centroid()
        key = f"({source_centroid[0]:.1f}, {source_centroid[1]:.1f})"
        source_counts[key] = source_counts.get(key, 0) + 1

    print(f"\n✓ Balanced Clustering Results:")
    for source, count in sorted(source_counts.items()):
        print(f"  Source at {source} → {count} destinations")

    # Verify balance
    counts = list(source_counts.values())
    max_count = max(counts)
    min_count = min(counts)
    print(f"\n  Balance: {min_count}-{max_count} split (difference: {max_count - min_count})")

    if max_count - min_count <= 1:
        print(f"  ✅ BALANCED: Sources differ by at most 1 destination")
    else:
        print(f"  ⚠️  IMBALANCED: Difference of {max_count - min_count} destinations")

    # Compare with unbalanced clustering
    print(f"\n" + "=" * 50)
    matcher_unbalanced = ClusteringMapper(balance_clusters=False)
    matched1_unbal, matched2_unbal = matcher_unbalanced.match(contours1.holes, contours2.holes)

    source_counts_unbal = {}
    for source_hole in matched1_unbal:
        source_centroid = source_hole.centroid()
        key = f"({source_centroid[0]:.1f}, {source_centroid[1]:.1f})"
        source_counts_unbal[key] = source_counts_unbal.get(key, 0) + 1

    print(f"\n✗ Unbalanced Clustering Results (for comparison):")
    for source, count in sorted(source_counts_unbal.items()):
        print(f"  Source at {source} → {count} destinations")

    counts_unbal = list(source_counts_unbal.values())
    max_count_unbal = max(counts_unbal)
    min_count_unbal = min(counts_unbal)
    print(f"\n  Balance: {min_count_unbal}-{max_count_unbal} split (difference: {max_count_unbal - min_count_unbal})")

    print(f"\n" + "=" * 50)
    print(f"\nConclusion: Balancing {'improved' if (max_count - min_count) < (max_count_unbal - min_count_unbal) else 'did not change'} the split")
    print()


if __name__ == "__main__":
    test_splitting_balance()
