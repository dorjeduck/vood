"""VElement composition approach - animated clip element"""

from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, RectangleState, SquareState
from vood.core import Color

# Create a scene
scene = VScene(width=400, height=400)

# Define an animated clip element (morphs from circle to square)
animated_clip = VElement(
    keystates=[
        CircleState(radius=50),
        CircleState(radius=100),
    ]
)

state = RectangleState(
    width=200,
    height=200,
    fill_color=Color("#FF6B6B"),
)

# Apply clip to a rectangle
clipped_rect = VElement(keystates=[state, state], clip_element=animated_clip)

scene.add_element(clipped_rect)

# Export
if __name__ == "__main__":
    from vood.vscene import VSceneExporter

    exporter = VSceneExporter(scene)
    exporter.to_mp4("clipping_composition", total_frames=60, framerate=30)
    print(
        "✓ VElement composition clipping example exported to clipping_composition.mp4"
    )
