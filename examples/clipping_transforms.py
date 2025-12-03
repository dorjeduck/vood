"""Clip transforms example - clips with position, rotation, scale"""

from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, RectangleState
from vood.core import Color

# Create a scene
scene = VScene(width=400, height=400)

# Rectangle clipped by a circle that is offset and scaled
# Demonstrates that clip shapes respect their own transforms
clipped_with_transforms = VElement(
    state=RectangleState(
        width=200,
        height=200,
        fill_color=Color("#FF6B6B"),
        clip_state=CircleState(
            x=40,          # Clip offset to the right
            y=-20,         # Clip offset upward
            radius=70,
            scale=1.2,     # Clip is scaled larger
            rotation=0     # Could also rotate (less visible for circles)
        )
    )
)

scene.add_element(clipped_with_transforms)

# Export
if __name__ == "__main__":
    from vood.vscene import VSceneExporter

    exporter = VSceneExporter(scene)
    exporter.export("clipping_transforms", formats=["svg"])
    print("✓ Clip transforms example exported to clipping_transforms.svg")
