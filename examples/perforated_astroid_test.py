"""Test astroid integration in PerforatedShape"""

from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.velement import VElement
from vood.component.state import PerforatedShapeState
from vood.component.renderer import PerforatedShapeRenderer
from vood.core.color import Color


def test_circle_with_astroid_holes():
    """Test circle with astroid holes"""
    print("Creating circle with astroid holes...")
    scene = VScene(width=400, height=400, background=Color("#1a1a2e"))

    state = PerforatedShapeState(
        x=0, y=0,
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "astroid", "radius": 30, "num_cusps": 4, "curvature": 0.7, "x": -40, "y": 0},
            {"type": "astroid", "radius": 25, "num_cusps": 5, "curvature": 0.6, "x": 40, "y": 0},
        ],
        fill_color=Color("#4ECDC4"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    renderer = PerforatedShapeRenderer()
    element = VElement(renderer=renderer, state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_circle_astroid_holes.svg")
    print("  ✓ Created: test_circle_astroid_holes.svg")


def test_astroid_with_circle_holes():
    """Test astroid outer shape with circular holes"""
    print("Creating astroid with circular holes...")
    scene = VScene(width=400, height=400, background=Color("#1a1a2e"))

    state = PerforatedShapeState(
        x=0, y=0,
        outer_shape={"type": "astroid", "radius": 100, "num_cusps": 6, "curvature": 0.7},
        holes=[
            {"type": "circle", "radius": 20, "x": 0, "y": 0},
        ],
        fill_color=Color("#FF6B6B"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    renderer = PerforatedShapeRenderer()
    element = VElement(renderer=renderer, state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_astroid_circle_holes.svg")
    print("  ✓ Created: test_astroid_circle_holes.svg")


def test_astroid_mixed_holes():
    """Test astroid with mixed hole shapes"""
    print("Creating astroid with mixed holes...")
    scene = VScene(width=400, height=400, background=Color("#1a1a2e"))

    state = PerforatedShapeState(
        x=0, y=0,
        outer_shape={"type": "astroid", "radius": 120, "num_cusps": 8, "curvature": 0.65},
        holes=[
            {"type": "circle", "radius": 15, "x": 0, "y": 0},
            {"type": "astroid", "radius": 18, "num_cusps": 3, "curvature": 0.8, "x": -50, "y": 0, "rotation": 30},
            {"type": "astroid", "radius": 18, "num_cusps": 3, "curvature": 0.8, "x": 50, "y": 0, "rotation": 30},
            {"type": "square", "size": 20, "x": 0, "y": -50, "rotation": 45},
            {"type": "square", "size": 20, "x": 0, "y": 50, "rotation": 45},
        ],
        fill_color=Color("#95E1D3"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    renderer = PerforatedShapeRenderer()
    element = VElement(renderer=renderer, state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_astroid_mixed_holes.svg")
    print("  ✓ Created: test_astroid_mixed_holes.svg")


def test_various_astroid_curvatures():
    """Test astroids with different curvatures as holes"""
    print("Creating shape with various astroid curvature holes...")
    scene = VScene(width=500, height=500, background=Color("#1a1a2e"))

    state = PerforatedShapeState(
        x=0, y=0,
        outer_shape={"type": "circle", "radius": 150},
        holes=[
            {"type": "astroid", "radius": 35, "num_cusps": 4, "curvature": 0.3, "x": -70, "y": -70},
            {"type": "astroid", "radius": 35, "num_cusps": 4, "curvature": 0.5, "x": 70, "y": -70},
            {"type": "astroid", "radius": 35, "num_cusps": 4, "curvature": 0.7, "x": -70, "y": 70},
            {"type": "astroid", "radius": 35, "num_cusps": 4, "curvature": 0.9, "x": 70, "y": 70},
        ],
        fill_color=Color("#AA96DA"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    renderer = PerforatedShapeRenderer()
    element = VElement(renderer=renderer, state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_astroid_curvatures_holes.svg")
    print("  ✓ Created: test_astroid_curvatures_holes.svg")


if __name__ == "__main__":
    print("\n=== Astroid in PerforatedShape Tests ===\n")
    test_circle_with_astroid_holes()
    test_astroid_with_circle_holes()
    test_astroid_mixed_holes()
    test_various_astroid_curvatures()
    print("\n✅ All astroid integration tests completed!\n")
