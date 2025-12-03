"""Scene-level clipping example - viewport clipping"""

from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, RectangleState
from vood.core import Color
from vood.layout.grid import grid

# Create a scene with scene-level clipping (circular viewport)
scene = VScene(
    width=400,
    height=400,
    #clip_state=CircleState(radius=150)
)

# Create multiple elements that will all be clipped by the scene viewport
states = [
    CircleState(radius=30, fill_color=Color(f"#{i*30:02x}0000"))
    for i in range(9)
]
positioned = grid(states, rows=3, cols=3, spacing_h=80, spacing_v=80)

for state in positioned:
    scene.add_element(VElement(state=state))

# Export
if __name__ == "__main__":
    from vood.vscene import VSceneExporter

    exporter = VSceneExporter(scene)
    exporter.export("clipping_scene", formats=["svg"])
    print("✓ Scene-level clipping example exported to clipping_scene.svg")
