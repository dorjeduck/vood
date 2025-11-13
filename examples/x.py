from vood.component import TextRenderer, TextState
from vood.component.renderer.triangle import TriangleRenderer
from vood.component.state.ring import RingState
from vood.component.state.square import SquareState
from vood.component.state.triangle import TriangleState
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.velement import VElement
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

    start_state = TriangleState(size=20)
    end_state = RingState(
        outer_radius=70,
        inner_radius=30,
    )
    middle_state = SquareState(size=20)

    triangle_element = VElement(
        keystates=[
            (0, start_state),
            (0.5, middle_state),
            (1, end_state),
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
        filename="x.mp4",
        total_frames=120,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
