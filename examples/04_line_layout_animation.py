from vood.components.text import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.state_functions import line_layout
from vood.utils.logger import configure_logging
from vood.velements import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter

configure_logging(level="INFO")


def main():

    # Create the scene
    scene = VScene(width=256, height=256, background="#000017")

    # Create text states for each number with consistent styling
    states = [
        TextState(
            text=str(num),
            font_family="Courier",
            font_size=20,
            color="#FDBE02",
        )
        for num in range(1, 10)
    ]

    # Arrange the numbers along a line for start and end positions
    start_states = line_layout(states, spacing=10, rotation=0)
    end_states = line_layout(states, spacing=30, rotation=135)

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # Create visual elements from states
    # VElements in Vood are the combination of one renderer and one or more states
    elements = [
        VElement(
            renderer=renderer,
            states=[start_state, end_state],
        )
        for start_state, end_state in zip(start_states, end_states)
    ]

    # Add all elements to the scene
    scene.add_elements(elements)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.INKSCAPE,
        output_dir="output/",
    )

    # Export to MP4 file
    exporter.to_mp4(
        filename="04_along_line_line",
        total_frames=60,
        framerate=30,
        width_px=512,
        num_thumbnails=10,
    )


if __name__ == "__main__":
    main()
