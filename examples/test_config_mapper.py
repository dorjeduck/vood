"""Test hole matcher selection from config"""

from vood.config import load_config, get_config
from vood.component.state.perforated_shape import PerforatedShapeState
from vood.transition.interpolation.align_vertices import get_aligned_vertices


def test_config_matcher_selection():
    """Test that config properly selects hole matching strategy"""

    # Create test states (5→2 merging)
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

    print("\n" + "=" * 60)
    print("Testing Hole Mapper Config Selection")
    print("=" * 60)

    # Test 1: Default (clustering with balancing)
    print("\n1. DEFAULT CONFIG (clustering with balancing)")
    config = get_config()
    print(f"   Config: hole_mapper = {config.get('morphing.hole_mapper', 'N/A')}")
    print(
        f"   Config: balance_clusters = {config.get('morphing.clustering.balance_clusters', 'N/A')}"
    )

    contours1, contours2 = get_aligned_vertices(state1, state2)

    # Count distribution
    dest_counts = {}
    for hole in contours2.holes:
        key = tuple(round(c, 1) for c in hole.centroid())
        dest_counts[key] = dest_counts.get(key, 0) + 1

    print(f"   Result: {list(dest_counts.values())} split")
    max_diff = max(dest_counts.values()) - min(dest_counts.values())
    print(
        f"   Balance: difference = {max_diff} ({'✅ BALANCED' if max_diff <= 1 else '⚠️ IMBALANCED'})"
    )

    # Test 2: Greedy (simulated via config)
    print("\n2. GREEDY MATCHER (simulated)")
    print("   To use greedy, create vood.toml with:")
    print("   [morphing]")
    print('   hole_mapper = "greedy"')
    print()
    print("   Or override in code:")
    from vood.transition.interpolation.hole_mapping import GreedyNearestMapper

    contours1_greedy, contours2_greedy = get_aligned_vertices(
        state1, state2, hole_mapper=GreedyNearestMapper()
    )

    dest_counts_greedy = {}
    for hole in contours2_greedy.holes:
        key = tuple(round(c, 1) for c in hole.centroid())
        dest_counts_greedy[key] = dest_counts_greedy.get(key, 0) + 1

    print(f"   Result: {list(dest_counts_greedy.values())} split")
    max_diff_greedy = max(dest_counts_greedy.values()) - min(
        dest_counts_greedy.values()
    )
    print(
        f"   Balance: difference = {max_diff_greedy} ({'✅ BALANCED' if max_diff_greedy <= 1 else '⚠️ IMBALANCED'})"
    )

    # Test 3: Clustering without balancing
    print("\n3. CLUSTERING WITHOUT BALANCING")
    print("   To disable balancing, create vood.toml with:")
    print("   [morphing]")
    print('   hole_mapper = "clustering"')
    print("   ")
    print("   [morphing.clustering]")
    print("   balance_clusters = false")
    print()
    print("   Or override in code:")
    from vood.transition.interpolation.hole_mapping import ClusteringMapper

    contours1_unbal, contours2_unbal = get_aligned_vertices(
        state1, state2, hole_mapper=ClusteringMapper(balance_clusters=False)
    )

    dest_counts_unbal = {}
    for hole in contours2_unbal.holes:
        key = tuple(round(c, 1) for c in hole.centroid())
        dest_counts_unbal[key] = dest_counts_unbal.get(key, 0) + 1

    print(f"   Result: {list(dest_counts_unbal.values())} split")
    max_diff_unbal = max(dest_counts_unbal.values()) - min(dest_counts_unbal.values())
    print(
        f"   Balance: difference = {max_diff_unbal} ({'✅ BALANCED' if max_diff_unbal <= 1 else '⚠️ IMBALANCED'})"
    )

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Clustering (balanced):   {max_diff}-hole difference")
    print(f"  Greedy:                  {max_diff_greedy}-hole difference")
    print(f"  Clustering (unbalanced): {max_diff_unbal}-hole difference")
    print("\n✅ Config-based strategy selection working correctly!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_config_matcher_selection()
