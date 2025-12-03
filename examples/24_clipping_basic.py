"""Basic clipping example - static clip-path"""

from vood.component.state.triangle import TriangleState
from vood.converter.converter_type import ConverterType
from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, RectangleState
from vood.core import Color
from vood.vscene import VSceneExporter

# Create a scene
scene = VScene(width=400, height=400)

# Rectangle clipped by a circle
clipped_rect = VElement(
    state=RectangleState(
        width=200,
        height=200,
        fill_color=Color("#FF6B6B"),
        clip_state=TriangleState(size=30, x=-50, rotation=90),
    )
)

scene.add_element(clipped_rect)

exporter = VSceneExporter(
    scene=scene,
    converter=ConverterType.PLAYWRIGHT,
    output_dir="output/",
)
exporter.export("24_clipping_basic", formats=["svg"])
