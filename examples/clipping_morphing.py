"""Morphing clip example - clip shape changes type"""

from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, SquareState, RectangleState, TriangleState
from vood.core import Color

# Create a scene
scene = VScene(width=400, height=400)

state = RectangleState(
    width=200,
    height=200,
    fill_color=Color("#4ECDC4"),
)

# Rectangle clipped by a shape that morphs from circle → square → triangle
# Demonstrates vertex-based morphing of clip shapes
# NOTE: property_keystates format is (time, value) with TIME FIRST
morphing_clip = VElement(
    keystates=[state, state],
    property_keystates={
        "clip_state": [
            (0.0, CircleState(radius=60)),
            (0.5, SquareState(size=100)),
            (1.0, TriangleState(size=120)),
        ]
    }
)

scene.add_element(morphing_clip)

# Export
if __name__ == "__main__":
    from vood.vscene import VSceneExporter

    exporter = VSceneExporter(scene)
    exporter.to_mp4("clipping_morphing", total_frames=90, framerate=30)
    print("✓ Morphing clip example exported to clipping_morphing.mp4")
