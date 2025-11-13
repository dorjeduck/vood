"""Quick test of PerforatedShape - various shape combinations"""

from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.velement import VElement
from vood.component.state import (
    PerforatedCircleState,
    PerforatedRectangleState,
    PerforatedPolygonState,
    PerforatedTriangleState,
    PerforatedEllipseState,
    Circle,
    Ellipse,
    Rectangle,
    Polygon,
)
from vood.core.color import Color


def test_circle_with_square_holes():
    """Test circle with square holes"""
    print("Creating circle with square holes...")
    scene = VScene(width=400, height=400, background=Color("#1a1a2e"))

    state = PerforatedCircleState(
        x=0,
        y=0,
        radius=80,
        holes=[
            Rectangle(width=35, height=35, x=-30, y=0, rotation=45),
            Rectangle(width=35, height=35, x=30, y=0, rotation=0),
        ],
        fill_color=Color("#4ECDC4"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    element = VElement(state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_perforated_circle_square_holes.svg")
    print("  ✓ Created: test_perforated_circle_square_holes.svg")


def test_rectangle_with_circular_holes():
    """Test rectangle with circular holes"""
    print("Creating rectangle with circular holes...")
    scene = VScene(width=400, height=400, background=Color("#1a1a2e"))

    state = PerforatedRectangleState(
        x=0,
        y=0,
        width=140,
        height=90,
        holes=[
            Circle(radius=20, x=-40, y=0),
            Circle(radius=20, x=0, y=0),
            Circle(radius=20, x=40, y=0),
        ],
        fill_color=Color("#FF6B6B"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    element = VElement(state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_perforated_rectangle_holes.svg")
    print("  ✓ Created: test_perforated_rectangle_holes.svg")


def test_triangle_with_triangle_holes():
    """Test triangle with triangular holes"""
    print("Creating triangle with triangular holes...")
    scene = VScene(width=400, height=400, background=Color("#1a1a2e"))

    state = PerforatedTriangleState(
        x=0,
        y=0,
        size=100,
        holes=[
            Polygon(num_sides=3, radius=25, x=0, y=-20, rotation=0),
            Polygon(num_sides=3, radius=20, x=-20, y=15, rotation=180),
            Polygon(num_sides=3, radius=20, x=20, y=15, rotation=180),
        ],
        fill_color=Color("#95E1D3"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    element = VElement(state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_perforated_triangle_holes.svg")
    print("  ✓ Created: test_perforated_triangle_holes.svg")


def test_hexagon_with_mixed_holes():
    """Test hexagon with different shaped holes"""
    print("Creating hexagon with mixed holes...")
    scene = VScene(width=400, height=400, background=Color("#1a1a2e"))

    state = PerforatedPolygonState(
        x=0,
        y=0,
        num_sides=6,
        size=90,
        holes=[
            Circle(radius=15, x=0, y=-30),
            Rectangle(width=20, height=20, x=-26, y=15, rotation=45),
            Polygon(num_sides=3, radius=18, x=26, y=15),
        ],
        fill_color=Color("#F38181"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    element = VElement(state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_perforated_hexagon_mixed.svg")
    print("  ✓ Created: test_perforated_hexagon_mixed.svg")


def test_ellipse_with_ellipse_holes():
    """Test ellipse with elliptical holes"""
    print("Creating ellipse with elliptical holes...")
    scene = VScene(width=400, height=400, background=Color("#1a1a2e"))

    state = PerforatedEllipseState(
        x=0,
        y=0,
        rx=100,
        ry=60,
        holes=[
            Ellipse(rx=25, ry=15, x=-40, y=0, rotation=0),
            Ellipse(rx=25, ry=15, x=40, y=0, rotation=0),
        ],
        fill_color=Color("#AA96DA"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    element = VElement(state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_perforated_ellipse_holes.svg")
    print("  ✓ Created: test_perforated_ellipse_holes.svg")


if __name__ == "__main__":
    print("\n=== PerforatedShape Tests ===\n")
    test_circle_with_square_holes()
    test_rectangle_with_circular_holes()
    test_triangle_with_triangle_holes()
    test_hexagon_with_mixed_holes()
    test_ellipse_with_ellipse_holes()
    print("\n✅ All tests completed successfully!\n")
