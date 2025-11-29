"""Hole Matching Strategy Showcase

Demonstrates 4 different hole matching strategies with the same transitions:
- SimpleMapper
- GreedyNearestMapper
- DiscreteMapper
- ClusteringMapper (if available)

Each strategy shows: State1 (3 holes) → State2 (5 holes) → State1 (3 holes)
This creates a clear comparison of how each strategy handles hole splitting and merging.
"""

from vood.component.state import PerforatedCircleState, Circle, Star
from vood.component.renderer.base_vertex import VertexRenderer
from vood.velement import VElement, Morphing
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color
from vood.core.logger import configure_logging
from vood.converter.converter_type import ConverterType

# Import hole matching strategies
from vood.transition.hole_mapping import (
    SimpleMapper,
    GreedyNearestMapper,
    DiscreteMapper,
)

# Try to import ClusteringMapper (might not be implemented yet)
try:
    from vood.transition.hole_mapping import ClusteringMapper
    HAS_CLUSTERING = True
except ImportError:
    HAS_CLUSTERING = False

configure_logging(level="INFO")

# Common visual style
FILL_COLOR = Color("#4ECDC4")
STROKE_COLOR = Color("#FFFFFF")
STROKE_WIDTH = 2
BG_COLOR = Color("#1a1a2e")


def create_test_states():
    """Create the two states used for all strategy tests

    Returns:
        tuple: (state1, state2) where state1 has 3 holes and state2 has 6 holes

    Uses asymmetric arrangement to expose greedy vs clustering differences:
    - State 1: 3 holes spread out (top-left, center, bottom-right)
    - State 2: 6 holes in TWO tight clusters (3 near top-left, 3 near bottom-right)

    Greedy will make poor matches: multiple holes from same cluster may map
    to same destination, ignoring that they should stay together as a group.

    Clustering will recognize the 2 spatial groups and map each group to
    the nearest destination, preserving group coherence.
    """

    # State 1: Circle with 3 circular holes SPREAD OUT
    state1 = PerforatedCircleState(
        radius=250,
        holes=[
            Circle(radius=35, x=-80, y=-80),    # Top-left
            Circle(radius=35, x=0, y=0),        # Center
            Circle(radius=35, x=80, y=80),      # Bottom-right
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # State 2: Circle with 6 star holes in TWO TIGHT CLUSTERS
    # Cluster A: 3 holes tightly grouped near top-left (-80, -80)
    # Cluster B: 3 holes tightly grouped near bottom-right (80, 80)
    state2 = PerforatedCircleState(
        radius=250,
        holes=[
            # Cluster A: 3 holes near top-left destination (-80, -80)
            Star(outer_radius=25, inner_radius=12, num_points=5, x=-95, y=-95, rotation=0),
            Star(outer_radius=25, inner_radius=12, num_points=5, x=-80, y=-70, rotation=72),
            Star(outer_radius=25, inner_radius=12, num_points=5, x=-65, y=-85, rotation=144),
            # Cluster B: 3 holes near bottom-right destination (80, 80)
            Star(outer_radius=25, inner_radius=12, num_points=5, x=65, y=85, rotation=216),
            Star(outer_radius=25, inner_radius=12, num_points=5, x=80, y=70, rotation=288),
            Star(outer_radius=25, inner_radius=12, num_points=5, x=95, y=95, rotation=0),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    return state1, state2


def create_strategy_showcase(strategy_name, matcher_instance, state1, state2, output_filename):
    """Create a video showcasing a specific hole matching strategy

    Args:
        strategy_name: Name of the strategy for display
        matcher_instance: Instance of the hole matcher (or None for default)
        state1: First state (3 holes)
        state2: Second state (5 holes)
        output_filename: Output MP4 filename
    """
    print(f"\nCreating showcase for {strategy_name}...")

    scene = VScene(width=800, height=800, background=BG_COLOR)

    # Create keystates: S1 → S2 → S1
    # Each transition takes 1/2 of the time (0.0 → 0.5 → 1.0)
    if matcher_instance is None:
        # Default strategy (no override needed)
        keystates = [
            (0.0, state1),
            (0.5, state2),
            (1.0, state1),
        ]
    else:
        # Use KeyState class with Morphing to specify custom mapper
        from vood.velement.keystate import KeyState

        keystates = [
            KeyState(state=state1, time=0.0),
            KeyState(state=state2, time=0.5, morphing=Morphing(hole_mapper=matcher_instance)),
            KeyState(state=state1, time=1.0, morphing=Morphing(hole_mapper=matcher_instance)),
        ]

    element = VElement(renderer=VertexRenderer(), keystates=keystates)
    scene.add_element(element)

    exporter = VSceneExporter(scene=scene, converter=ConverterType.PLAYWRIGHT)
    exporter.to_mp4(
        filename=output_filename,
        total_frames=90,  # 30 fps * 3 seconds
        framerate=30,
        png_width_px=800,
    )

    print(f"  ✓ Created: {output_filename}")


def main():
    print("\n" + "="*70)
    print("  Hole Matching Strategy Showcase")
    print("  Comparing: Simple, Greedy, Discrete, Clustering")
    print("="*70)

    # Create the test states
    state1, state2 = create_test_states()

    print(f"\nState 1: Circle with 3 circular holes (spread out)")
    print(f"State 2: Circle with 6 star holes (2 tight clusters)")
    print(f"Animation: S1 → S2 → S1 for each strategy")
    print(f"\nAsymmetric setup to differentiate strategies:")
    print(f"  - Greedy: matches holes individually by nearest distance")
    print(f"  - Clustering: recognizes spatial groups and keeps them together\n")

    # Strategy 1: SimpleMapper
    create_strategy_showcase(
        strategy_name="SimpleMapper",
        matcher_instance=SimpleMapper(),
        state1=state1,
        state2=state2,
        output_filename="25_strategy_simple.mp4"
    )

    # Strategy 2: GreedyNearestMapper (default)
    create_strategy_showcase(
        strategy_name="GreedyNearestMapper",
        matcher_instance=GreedyNearestMapper(),
        state1=state1,
        state2=state2,
        output_filename="25_strategy_greedy.mp4"
    )

    # Strategy 3: DiscreteMapper
    create_strategy_showcase(
        strategy_name="DiscreteMapper",
        matcher_instance=DiscreteMapper(),
        state1=state1,
        state2=state2,
        output_filename="25_strategy_discrete.mp4"
    )

    # Strategy 4: ClusteringMapper (if available)
    if HAS_CLUSTERING:
        create_strategy_showcase(
            strategy_name="ClusteringMapper",
            matcher_instance=ClusteringMapper(),
            state1=state1,
            state2=state2,
            output_filename="25_strategy_clustering.mp4"
        )
    else:
        print(f"\n⚠️  ClusteringMapper not available (not implemented yet)")

    print("\n" + "="*70)
    print("✅ Hole Matching Strategy Showcase Complete!")
    print("="*70)
    print("\nGenerated files:")
    print("  • 25_strategy_simple.mp4      - SimpleMapper")
    print("  • 25_strategy_greedy.mp4      - GreedyNearestMapper")
    print("  • 25_strategy_discrete.mp4    - DiscreteMapper")
    if HAS_CLUSTERING:
        print("  • 25_strategy_clustering.mp4  - ClusteringMapper")
    print("\nEach video shows: 3 holes → 6 holes (2 clusters) → 3 holes")
    print("Compare them side-by-side to see strategy differences!\n")


if __name__ == "__main__":
    main()
