"""Animated masking example - fading mask effect"""

from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, RectangleState
from vood.core import Color

# Create a scene
scene = VScene(width=400, height=400)

state = RectangleState(
    width=200,
    height=200,
    fill_color=Color("#FF6B6B"),
)

# Rectangle with animated mask (opacity changes over time)
# Creates a fade-in effect
animated_mask = VElement(
    keystates=[state, state],
    #property_keystates={
    #    "mask_state": [
    #        CircleState(radius=80, fill_color=Color("#FFFFFF"), opacity=0.0),
    #        CircleState(radius=20, fill_color=Color("#FFFFFF"), opacity=1.0),
    #    ]
    #},
)

scene.add_element(animated_mask)

# Export
if __name__ == "__main__":
    from vood.vscene import VSceneExporter

    exporter = VSceneExporter(scene)
    exporter.to_mp4("masking_animated", total_frames=30, framerate=30)
    print("✓ Animated masking example exported to masking_animated.mp4")
