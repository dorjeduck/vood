"""Basic clipping example - static clip-path"""

from dataclasses import replace
from vood.component.state.triangle import TriangleState
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, RectangleState
from vood.core import Color
from vood.vscene import VSceneExporter

configure_logging(level="INFO")

# Create a scene
scene = VScene(width=400, height=400)

s1 = RectangleState(
    width=200,
    height=200,
    fill_color=Color("#FF6B6B"),
    clip_state=CircleState(radius=30),
)

s2 = replace(s1, clip_state=CircleState(radius=60))


# Rectangle clipped by a circle
clipped_rect = VElement(
    keystates=[s1, s2],
)

scene.add_element(clipped_rect)

exporter = VSceneExporter(
    scene=scene,
    converter=ConverterType.PLAYWRIGHT,
    output_dir="output/",
)

exporter.to_mp4(
    filename="27_clipping_animated.mp4",
    total_frames=30,
    framerate=30,
    png_width_px=1024,
    num_thumbnails=100,
)
