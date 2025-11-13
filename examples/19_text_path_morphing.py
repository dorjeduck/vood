from dataclasses import replace
from vood.component import PathTextRenderer, PathTextState
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color

configure_logging(level="INFO")

START_COLOR = Color("#FDBE02")
END_COLOR = Color("#AA0000")

START_PATH = "M -100,0 L 100,0"
END_PATH = "M -100,0 C -50,-100 50,100 100,0"


def main():

    # Create the scene
    scene = VScene(width=256, height=256, background=Color("#000017"))

    # Create text states for each number with consistent styling
    # These states will be the starting point of the animation

    start_state = PathTextState(
        text="Empty Mirror",
        font_family="Courier New",
        font_size=22,
        data=START_PATH,
        fill_color=START_COLOR,
    )

    end_state = replace(
        start_state, data=END_PATH, letter_spacing=6, fill_color=END_COLOR
    )

    renderer = PathTextRenderer()

    element = VElement(renderer=renderer, keystates=[start_state, end_state])

    scene.add_element(element)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to mp4
    exporter.to_mp4(
        filename="19_text_path_morphing",
        total_frames=60,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
