from dataclasses import replace

from vood.component.renderer.path import PathRenderer
from vood.component.state.path import PathState
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color

configure_logging(level="INFO")

START_COLOR = Color("#FDBE02")
END_COLOR = Color("#AA0000")

START_SHAPE = "M 0,-50 L 14.43,-15.45 L 47.55,-15.45 L 23.56,6.18 L 36.99,40.45 L 0,20 L -36.99,40.45 L -23.56,6.18 L -47.55,-15.45 L -14.43,-15.45 Z"
END_SHAPE = "M 50,0 C 50,27.6 27.6,50 0,50 C -27.6,50 -50,27.6 -50,0 C -50,-27.6 -27.6,-50 0,-50 C 27.6,-50 50,-27.6 50,0 Z"


def main():

    # Create the scene
    scene = VScene(width=256, height=256, background=Color("#000017"))

    start_state = PathState(
        data=START_SHAPE,
        fill_color=START_COLOR,
    )

    end_state = replace(
        start_state,
        data=END_SHAPE,
        fill_color=END_COLOR,
    )

    # Create a text renderer for all numbers
    renderer = PathRenderer()

    element = VElement(
        renderer=renderer,
        keystates=[start_state, end_state],
    )

    # Add all elements to the scene
    scene.add_element(element)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to mp4
    exporter.to_mp4(
        filename="20_shape_morphing",
        total_frames=60,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
