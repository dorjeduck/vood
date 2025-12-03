"""Reusable clip example - one clip applied to multiple elements"""

from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, RectangleState
from vood.core import Color

# Create a scene
scene = VScene(width=400, height=400)

# Define a single clip element
clip = VElement(state=CircleState(radius=60))

# Apply the same clip to multiple elements at different positions
rect1 = VElement(
    state=RectangleState(
        x=-80, y=0,
        width=120, height=120,
        fill_color=Color("#FF6B6B"),
    ),
    clip_element=clip
)

rect2 = VElement(
    state=RectangleState(
        x=80, y=0,
        width=120, height=120,
        fill_color=Color("#4ECDC4"),
    ),
    clip_element=clip  # Reuse same clip
)

scene.add_element(rect1)
scene.add_element(rect2)

# Export
if __name__ == "__main__":
    from vood.vscene import VSceneExporter

    exporter = VSceneExporter(scene)
    exporter.export("clipping_reusable", formats=["svg"])
    print("✓ Reusable clip example exported to clipping_reusable.svg")
