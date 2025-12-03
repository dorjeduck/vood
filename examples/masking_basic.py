"""Basic masking example - opacity-based transparency"""

from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, RectangleState
from vood.core import Color

# Create a scene
scene = VScene(width=400, height=400)

# Rectangle with a mask (uses opacity for gradual transparency)
# Unlike clip-path (binary), masks support gradual fading
masked_rect = VElement(
    state=RectangleState(
        width=200,
        height=200,
        fill_color=Color("#4ECDC4"),
        mask_state=CircleState(
            radius=80,
            fill_color=Color("#FFFFFF"),  # White = visible
            opacity=0.7  # Partial opacity = semi-transparent
        )
    )
)

scene.add_element(masked_rect)

# Export
if __name__ == "__main__":
    from vood.vscene import VSceneExporter

    exporter = VSceneExporter(scene)
    exporter.export("masking_basic", formats=["svg"])
    print("✓ Basic masking example exported to masking_basic.svg")
