"""Example: Per-Segment Hole Mapper Overrides

Demonstrates using different hole matching strategies for different animation
segments within the same element, showcasing the flexibility of per-segment
alignment configuration.
"""

from vood.vscene import VScene
from vood.velement import VElement
from vood.component.state import PerforatedShapeState
from vood.core.color import Color
from vood.transition import easing
from vood.transition.interpolation.hole_mapping import (
    SimpleMapper,
    DiscreteMapper,
    GreedyNearestMapper,
    ClusteringMapper,
)


def create_animation():
    """Create animation showing different hole matching strategies per segment"""

    # State 1: Single centered hole
    state1 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 20, "x": 0, "y": 0},
        ],
        fill_color=Color("#FDBE02"),
        fill_opacity=1.0,
        stroke_color=Color("#000000"),
        stroke_width=2,
    )

    # State 2: Five holes in cross pattern
    state2 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 12, "x": 0, "y": 0},  # center
            {"type": "circle", "radius": 12, "x": -50, "y": 0},  # left
            {"type": "circle", "radius": 12, "x": 50, "y": 0},  # right
            {"type": "circle", "radius": 12, "x": 0, "y": -50},  # top
            {"type": "circle", "radius": 12, "x": 0, "y": 50},  # bottom
        ],
        fill_color=Color("#FDBE02"),
        fill_opacity=1.0,
        stroke_color=Color("#000000"),
        stroke_width=2,
    )

    # State 3: Two diagonal holes
    state3 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 18, "x": -60, "y": -60},
            {"type": "circle", "radius": 18, "x": 60, "y": 60},
        ],
        fill_color=Color("#FDBE02"),
        fill_opacity=1.0,
        stroke_color=Color("#000000"),
        stroke_width=2,
    )

    # State 4: Three horizontal holes
    state4 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 15, "x": -60, "y": 0},
            {"type": "circle", "radius": 15, "x": 0, "y": 0},
            {"type": "circle", "radius": 15, "x": 60, "y": 0},
        ],
        fill_color=Color("#FDBE02"),
        fill_opacity=1.0,
        stroke_color=Color("#000000"),
        stroke_width=2,
    )

    # Create element with per-segment hole matcher overrides
    element = VElement(
        keystates=[
            (0.0, state1),
            # Segment 1→2: Use SimpleMapper (all old disappear, all new appear)
            (0.25, state2, None, {"hole_mapper": SimpleMapper()}),
            # Segment 2→3: Use DiscreteMapper (some move, some disappear)
            (
                0.50,
                state3,
                {"opacity": easing.in_out_cubic},
                {"hole_mapper": DiscreteMapper()},
            ),
            # Segment 3→4: Use GreedyNearestMapper (fast greedy matching)
            (0.75, state4, None, {"hole_mapper": GreedyNearestMapper()}),
            # Segment 4→1: Use ClusteringMapper (balanced spatial grouping - default)
            # No override specified, will use config default
            (1.0, state1),
        ]
    )

    scene = VScene(width=800, height=800)
    scene.add(element)

    return scene


def main():
    """Generate animation demonstrating per-segment hole matching"""

    scene = create_animation()

    print("Generating animation with per-segment hole matchers...")
    print("\nSegment strategies:")
    print("  0.00→0.25: SimpleMapper (all disappear/appear)")
    print("  0.25→0.50: DiscreteMapper (selective matching)")
    print("  0.50→0.75: GreedyNearestMapper (fast greedy)")
    print("  0.75→1.00: ClusteringMapper (default from config)")

    # Export to SVG for inspection
    scene.export("segment_hole_mapper.svg")
    print("\n✅ Exported to segment_hole_mapper.svg")

    # Export to animated format
    try:
        scene.to_mp4(
            "segment_hole_mapper.mp4", total_frames=120, framerate=30, png_width_px=800
        )
        print("✅ Exported to segment_hole_mapper.mp4")
    except Exception as e:
        print(f"⚠️  Could not export MP4: {e}")
        print("   (This is normal if no converter is installed)")


if __name__ == "__main__":
    main()
