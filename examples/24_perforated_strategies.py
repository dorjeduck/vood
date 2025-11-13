"""Advanced perforated shapes example demonstrating hole matching strategies

This example showcases:
1. All 6 perforated outer shape types (Circle, Star, Ellipse, Rectangle, Polygon, Triangle)
2. Different hole matching strategies (GreedyNearest, Simple, Discrete)
3. Complex hole count transitions (merging, splitting, creation, destruction)
4. Mixed hole shapes (circles, stars, polygons, astroids)
"""

from vood.animation.atomic import sequential_transition, trim
from vood.component.renderer.base_vertex import VertexRenderer
from vood.component.state import (
    PerforatedCircleState,
    PerforatedStarState,
    PerforatedEllipseState,
    PerforatedRectangleState,
    PerforatedPolygonState,
    PerforatedTriangleState,
    CircleState,
    Astroid,
    Ellipse,
    Polygon,
    Circle,
    Star,
)
# Note: Strategy overrides would require KeyState class
# from vood.transition.interpolation.hole_mapping import (
#     GreedyNearestMapper,
#     SimpleMapper,
#     DiscreteMapper,
# )
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color

configure_logging(level="INFO")

FILL_COLOR = Color("#4ECDC4")
STROKE_COLOR = Color("#FFFFFF")
STROKE_WIDTH = 2


def create_perforated_showcase():
    """Create a comprehensive showcase of perforated shapes with different strategies"""

    scene = VScene(width=1024, height=1024, background=Color("#1a1a2e"))

    # State 1: Circle with 3 circular holes (starting point)
    s1 = PerforatedCircleState(
        radius=300,
        holes=[
            Circle(radius=40, x=0, y=-120),
            Circle(radius=40, x=-104, y=60),
            Circle(radius=40, x=104, y=60),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # State 2: Star with 5 star holes (3 holes → 5 holes, splitting)
    # Uses GreedyNearestMapper by default
    s2 = PerforatedStarState(
        outer_radius=350,
        inner_radius=175,
        num_points=5,
        holes=[
            Star(outer_radius=30, inner_radius=15, num_points=5, x=0, y=-140, rotation=0),
            Star(outer_radius=30, inner_radius=15, num_points=5, x=-120, y=-50, rotation=72),
            Star(outer_radius=30, inner_radius=15, num_points=5, x=-75, y=120, rotation=144),
            Star(outer_radius=30, inner_radius=15, num_points=5, x=75, y=120, rotation=216),
            Star(outer_radius=30, inner_radius=15, num_points=5, x=120, y=-50, rotation=288),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # State 3: Ellipse with 2 elliptical holes (5 holes → 2 holes, merging)
    s3 = PerforatedEllipseState(
        rx=320,
        ry=200,
        holes=[
            Ellipse(rx=50, ry=30, x=-100, y=0, rotation=0),
            Ellipse(rx=50, ry=30, x=100, y=0, rotation=0),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # State 4: Rectangle with 4 square holes (2 holes → 4 holes, splitting)
    s4 = PerforatedRectangleState(
        width=500,
        height=350,
        holes=[
            Polygon(num_sides=4, radius=40, x=-100, y=-75, rotation=45),
            Polygon(num_sides=4, radius=40, x=100, y=-75, rotation=45),
            Polygon(num_sides=4, radius=40, x=-100, y=75, rotation=45),
            Polygon(num_sides=4, radius=40, x=100, y=75, rotation=45),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # State 5: Hexagon with 6 astroid holes (4 holes → 6 holes)
    s5 = PerforatedPolygonState(
        num_sides=6,
        size=280,
        holes=[
            Astroid(radius=35, num_cusps=4, curvature=0.7, x=0, y=-140, rotation=0),
            Astroid(radius=35, num_cusps=4, curvature=0.7, x=120, y=-70, rotation=60),
            Astroid(radius=35, num_cusps=4, curvature=0.7, x=120, y=70, rotation=120),
            Astroid(radius=35, num_cusps=4, curvature=0.7, x=0, y=140, rotation=180),
            Astroid(radius=35, num_cusps=4, curvature=0.7, x=-120, y=70, rotation=240),
            Astroid(radius=35, num_cusps=4, curvature=0.7, x=-120, y=-70, rotation=300),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # State 6: Triangle with 1 hole (6 holes → 1 hole, extreme merging)
    s6 = PerforatedTriangleState(
        size=300,
        holes=[
            Circle(radius=60, x=0, y=30),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # State 7: Circle with no holes (1 hole → 0 holes, destruction)
    s7 = PerforatedCircleState(
        radius=300,
        holes=[],  # No holes!
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # State 8: Plain circle (for comparison - morph to non-perforated)
    s8 = CircleState(
        radius=300,
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # Create animation sequence demonstrating various transitions
    # s1 (3 holes) → s2 (5 holes) → s3 (2 holes) → s4 (4 holes) →
    # s5 (6 holes) → s6 (1 hole) → s7 (0 holes) → s8 (solid) → back to s1
    states = [s1, s2, s3, s4, s5, s6, s7, s8, s1]

    # Create keystates with timing
    keystates = sequential_transition(states, trim, 0.5)

    # Use vertex renderer for morphing
    element = VElement(renderer=VertexRenderer(), keystates=keystates)
    scene.add_element(element)

    # Export animation
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
    )

    exporter.to_mp4(
        filename="24_perforated_strategies.mp4",
        total_frames=120,
        framerate=30,
        png_width_px=1024,
    )

    print("\n✅ Created: 24_perforated_strategies.mp4")
    print("   Demonstrates: 6 shape types, hole merging/splitting, creation/destruction")


def create_strategy_comparison():
    """Create different morphing sequences showing hole transitions

    Note: All use default GreedyNearestMapper strategy.
    To use different strategies, KeyState class with alignment dict would be needed.
    """

    print("\n=== Creating Hole Transition Examples ===\n")

    # Common start and end states for comparison
    start_state = PerforatedCircleState(
        radius=250,
        holes=[
            Circle(radius=30, x=-80, y=-80),
            Circle(radius=30, x=80, y=-80),
            Circle(radius=30, x=0, y=80),
        ],
        fill_color=Color("#FF6B6B"),
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    end_state = PerforatedStarState(
        outer_radius=300,
        inner_radius=150,
        num_points=5,
        holes=[
            Star(outer_radius=25, inner_radius=12, num_points=5, x=0, y=-100),
            Star(outer_radius=25, inner_radius=12, num_points=5, x=95, y=-30),
            Star(outer_radius=25, inner_radius=12, num_points=5, x=60, y=80),
            Star(outer_radius=25, inner_radius=12, num_points=5, x=-60, y=80),
            Star(outer_radius=25, inner_radius=12, num_points=5, x=-95, y=-30),
        ],
        fill_color=Color("#FF6B6B"),
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    # Example 1: 3 holes → 5 holes (splitting)
    print("Creating: 3 to 5 holes transition...")
    scene1 = VScene(width=800, height=800, background=Color("#1a1a2e"))
    keystates1 = [start_state, end_state]
    element1 = VElement(renderer=VertexRenderer(), keystates=keystates1)
    scene1.add_element(element1)

    exporter1 = VSceneExporter(scene=scene1, converter=ConverterType.PLAYWRIGHT)
    exporter1.to_mp4(
        filename="24_transition_3_to_5.mp4",
        total_frames=60,
        framerate=30,
        png_width_px=800,
    )
    print("  ✓ Created: 24_transition_3_to_5.mp4 (3 holes splitting to 5)")

    print("\n✅ Hole transition example created!")


def create_extreme_cases():
    """Create examples of extreme hole count changes"""

    print("\n=== Creating Extreme Case Examples ===\n")

    # Extreme case 1: Many holes → Few holes (10 → 2)
    print("Creating: Many-to-few holes example...")

    start_many = PerforatedCircleState(
        radius=280,
        holes=[
            Circle(radius=20, x=0, y=-120),
            Circle(radius=20, x=85, y=-85),
            Circle(radius=20, x=120, y=0),
            Circle(radius=20, x=85, y=85),
            Circle(radius=20, x=0, y=120),
            Circle(radius=20, x=-85, y=85),
            Circle(radius=20, x=-120, y=0),
            Circle(radius=20, x=-85, y=-85),
            Circle(radius=15, x=-40, y=0),
            Circle(radius=15, x=40, y=0),
        ],
        fill_color=Color("#9B59B6"),
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    end_few = PerforatedEllipseState(
        rx=300,
        ry=180,
        holes=[
            Ellipse(rx=60, ry=40, x=-100, y=0),
            Ellipse(rx=60, ry=40, x=100, y=0),
        ],
        fill_color=Color("#9B59B6"),
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    scene = VScene(width=800, height=800, background=Color("#1a1a2e"))
    keystates = [(0.0, start_many), (1.0, end_few)]
    element = VElement(renderer=VertexRenderer(), keystates=keystates)
    scene.add_element(element)

    exporter = VSceneExporter(scene=scene, converter=ConverterType.PLAYWRIGHT)
    exporter.to_mp4(
        filename="24_extreme_many_to_few.mp4",
        total_frames=90,
        framerate=30,
        png_width_px=800,
    )
    print("  ✓ Created: 24_extreme_many_to_few.mp4 (10 holes → 2 holes)")

    # Extreme case 2: Zero holes → Many holes (0 → 8)
    print("Creating: Zero-to-many holes example...")

    start_zero = PerforatedPolygonState(
        num_sides=8,
        size=280,
        holes=[],  # No holes
        fill_color=Color("#3498DB"),
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    end_many = PerforatedPolygonState(
        num_sides=8,
        size=280,
        holes=[
            Polygon(num_sides=3, radius=30, x=0, y=-120, rotation=0),
            Polygon(num_sides=3, radius=30, x=85, y=-85, rotation=45),
            Polygon(num_sides=3, radius=30, x=120, y=0, rotation=90),
            Polygon(num_sides=3, radius=30, x=85, y=85, rotation=135),
            Polygon(num_sides=3, radius=30, x=0, y=120, rotation=180),
            Polygon(num_sides=3, radius=30, x=-85, y=85, rotation=225),
            Polygon(num_sides=3, radius=30, x=-120, y=0, rotation=270),
            Polygon(num_sides=3, radius=30, x=-85, y=-85, rotation=315),
        ],
        fill_color=Color("#3498DB"),
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    scene = VScene(width=800, height=800, background=Color("#1a1a2e"))
    keystates = [(0.0, start_zero), (1.0, end_many)]
    element = VElement(renderer=VertexRenderer(), keystates=keystates)
    scene.add_element(element)

    exporter = VSceneExporter(scene=scene, converter=ConverterType.PLAYWRIGHT)
    exporter.to_mp4(
        filename="24_extreme_zero_to_many.mp4",
        total_frames=90,
        framerate=30,
        png_width_px=800,
    )
    print("  ✓ Created: 24_extreme_zero_to_many.mp4 (0 holes → 8 holes)")

    print("\n✅ All extreme case examples created!")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  Perforated Shapes: Advanced Demonstrations")
    print("="*70)

    # Main comprehensive showcase
    print("\n1. Creating comprehensive showcase...")
    create_perforated_showcase()

    # Hole transitions
    print("\n2. Creating hole transition examples...")
    create_strategy_comparison()

    # Extreme cases
    print("\n3. Creating extreme cases...")
    create_extreme_cases()

    print("\n" + "="*70)
    print("✅ All demonstrations complete!")
    print("="*70)
    print("\nGenerated files:")
    print("  • 24_perforated_strategies.mp4     - Main showcase (all 6 shapes)")
    print("  • 24_transition_3_to_5.mp4         - 3 holes → 5 holes")
    print("  • 24_extreme_many_to_few.mp4       - 10 holes → 2 holes")
    print("  • 24_extreme_zero_to_many.mp4      - 0 holes → 8 holes")
    print("\n")
