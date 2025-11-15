from vood.components.renderer import MorphRenderer
from vood.components.states import MorphTriangleState
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.velements import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color
from dataclasses import replace

configure_logging(level="INFO")

START_COLOR = Color("#ff0000")
END_COLOR = Color("#0000ff")


def main():

    # Create the scene
    scene = VScene(width=256, height=256, background=Color("#000017"))

    triange_start_state = MorphTriangleState(x=-70, size=20)
    triange_end_state = replace(triange_start_state, x=70, scale=2)

    triangle_element = VElement(
        renderer=MorphRenderer(),
        keystates=[
            (0, triange_start_state),
            (0.125, triange_start_state),
            (0.875, triange_end_state),
            (1, triange_end_state),
        ],
        property_keystates={
            "fill_color": [(0, START_COLOR), (0.5, START_COLOR), (1, END_COLOR)]
        },
    )

    scene.add_element(triangle_element)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.CAIROSVG,
        output_dir="output/",
    )

    # Export to PNG file
    exporter.to_mp4(
        filename="y.mp4",
        total_frames=120,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
