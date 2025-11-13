"""Test of Astroid - star-like shape with inward-curving cusps"""

from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.velement import VElement
from vood.component.state import AstroidState
from vood.component.renderer import AstroidRenderer
from vood.core.color import Color


def test_classic_astroid():
    """Test classic 4-cusp astroid"""
    print("Creating classic 4-cusp astroid...")
    scene = VScene(width=400, height=400, background=Color("#1a1a2e"))

    state = AstroidState(
        x=0, y=0,
        radius=80,
        num_cusps=4,
        curvature=0.7,
        fill_color=Color("#FF6B6B"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    renderer = AstroidRenderer()
    element = VElement(renderer=renderer, state=state)
    scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_astroid_4cusps.svg")
    print("  ✓ Created: test_astroid_4cusps.svg")


def test_various_cusps():
    """Test astroids with different numbers of cusps"""
    print("Creating astroids with different cusp counts...")
    scene = VScene(width=1200, height=300, background=Color("#1a1a2e"))

    configs = [
        {"num_cusps": 3, "x": -450, "color": "#FF6B6B"},
        {"num_cusps": 4, "x": -225, "color": "#4ECDC4"},
        {"num_cusps": 5, "x": 0, "color": "#95E1D3"},
        {"num_cusps": 6, "x": 225, "color": "#F38181"},
        {"num_cusps": 8, "x": 450, "color": "#AA96DA"},
    ]

    for config in configs:
        state = AstroidState(
            x=config["x"],
            y=0,
            radius=60,
            num_cusps=config["num_cusps"],
            curvature=0.7,
            fill_color=Color(config["color"]),
            stroke_color=Color("#FFFFFF"),
            stroke_width=2,
        )
        renderer = AstroidRenderer()
        element = VElement(renderer=renderer, state=state)
        scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_astroid_cusps.svg")
    print("  ✓ Created: test_astroid_cusps.svg")


def test_various_curvatures():
    """Test astroids with different curvature values"""
    print("Creating astroids with different curvatures...")
    scene = VScene(width=1000, height=300, background=Color("#1a1a2e"))

    curvatures = [0.3, 0.5, 0.7, 0.9]
    positions = [-300, -100, 100, 300]

    for curv, x_pos in zip(curvatures, positions):
        state = AstroidState(
            x=x_pos,
            y=0,
            radius=60,
            num_cusps=5,
            curvature=curv,
            fill_color=Color("#4ECDC4"),
            stroke_color=Color("#FFFFFF"),
            stroke_width=2,
        )
        renderer = AstroidRenderer()
        element = VElement(renderer=renderer, state=state)
        scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("test_astroid_curvatures.svg")
    print("  ✓ Created: test_astroid_curvatures.svg")


if __name__ == "__main__":
    print("\n=== Astroid Tests ===\n")
    test_classic_astroid()
    test_various_cusps()
    test_various_curvatures()
    print("\n✅ All tests completed successfully!\n")
