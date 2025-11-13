"""Demo of PolyRing - generic polygon rings with customizable edges and rotation"""

from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.velement import VElement
from vood.component.state import PolyRingState
from vood.component.renderer import PolyRingRenderer
from vood.core.color import Color

# Create different polygon rings
def create_static_demo():
    """Static demo showing different polygon types"""
    scene = VScene(width=800, height=400, background=Color("#1a1a2e"))

    states = [
        # Triangle ring
        PolyRingState(
            x=-300, y=0,
            outer_size=60, inner_size=30,
            num_edges=3,
            fill_color=Color("#FF6B6B"),
            stroke_color=Color.NONE,
        ),
        # Square ring
        PolyRingState(
            x=-150, y=0,
            outer_size=60, inner_size=30,
            num_edges=4,
            fill_color=Color("#4ECDC4"),
            stroke_color=Color.NONE,
        ),
        # Pentagon ring
        PolyRingState(
            x=0, y=0,
            outer_size=60, inner_size=30,
            num_edges=5,
            fill_color=Color("#95E1D3"),
            stroke_color=Color.NONE,
        ),
        # Hexagon ring
        PolyRingState(
            x=150, y=0,
            outer_size=60, inner_size=30,
            num_edges=6,
            fill_color=Color("#F38181"),
            stroke_color=Color.NONE,
        ),
        # Octagon ring
        PolyRingState(
            x=300, y=0,
            outer_size=60, inner_size=30,
            num_edges=8,
            fill_color=Color("#AA96DA"),
            stroke_color=Color.NONE,
        ),
    ]

    for state in states:
        renderer = PolyRingRenderer()
        element = VElement(renderer=renderer, state=state)
        scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("poly_ring_static.svg")
    print("Created: poly_ring_static.svg")


def create_rotation_demo():
    """Demo showing inner rotation and whole shape rotation"""
    scene = VScene(width=800, height=400, background=Color("#1a1a2e"))

    # Hexagon with rotating inner hole
    state1 = PolyRingState(
        x=-200, y=0,
        outer_size=70, inner_size=35,
        num_edges=6,
        inner_rotation=30,  # Inner rotated 30°
        fill_color=Color("#FF6B6B"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    # Pentagon with whole shape rotated
    state2 = PolyRingState(
        x=0, y=0,
        outer_size=70, inner_size=35,
        num_edges=5,
        rotation=36,  # Whole shape rotated (360/5 = 72, half = 36)
        inner_rotation=0,
        fill_color=Color("#4ECDC4"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    # Square with diagonal orientation (whole shape) and inner rotation
    state3 = PolyRingState(
        x=200, y=0,
        outer_size=70, inner_size=35,
        num_edges=4,
        rotation=45,  # Whole shape rotated to diamond
        inner_rotation=0,
        fill_color=Color("#95E1D3"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    for state in [state1, state2, state3]:
        renderer = PolyRingRenderer()
        element = VElement(renderer=renderer, state=state)
        scene.add_element(element)

    exporter = VSceneExporter(scene)
    exporter.export("poly_ring_rotation.svg")
    print("Created: poly_ring_rotation.svg")


def create_animation_demo():
    """Animated demo showing morphing and rotation"""
    scene = VScene(width=600, height=600, background=Color("#1a1a2e"))

    # Morph from triangle to hexagon and back with rotation
    start_state = PolyRingState(
        x=0, y=0,
        outer_size=80, inner_size=40,
        num_edges=3,
        inner_rotation=0,
        fill_color=Color("#FF6B6B"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    mid_state = PolyRingState(
        x=0, y=0,
        outer_size=100, inner_size=30,
        num_edges=6,
        inner_rotation=30,
        fill_color=Color("#4ECDC4"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    end_state = PolyRingState(
        x=0, y=0,
        outer_size=80, inner_size=40,
        num_edges=3,
        inner_rotation=60,
        rotation=120,  # Rotate whole shape at the end
        fill_color=Color("#95E1D3"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    renderer = PolyRingRenderer()
    element = VElement(renderer=renderer, keystates=[start_state, mid_state, end_state])
    scene.add_element(element)

    # Export animation
    exporter = VSceneExporter(scene)
    exporter.to_mp4(
        output_filename="poly_ring_animation.mp4",
        total_frames=120,
        framerate=30,
        png_width_px=600,
    )
    print("Created: poly_ring_animation.mp4")


if __name__ == "__main__":
    print("Generating PolyRing demos...")
    create_static_demo()
    create_rotation_demo()
    # Uncomment to create animation (requires video export setup)
    # create_animation_demo()
    print("Done!")
