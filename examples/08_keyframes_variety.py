from dataclasses import replace

from vood.components.text import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.state_functions import line_layout
from vood.transitions.easing import Easing
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
    start_states = line_layout(states, center_x=-100, spacing=20, rotation=90)
    middle_states = line_layout(states, spacing=20, rotation=90)
    end_states = line_layout(states, center_x=100, spacing=20, rotation=90)

    # lets animate also a change of color
    middle_states = [replace(state, color="#d88023") for state in end_states]
    end_states = [replace(state, color="#AA0000") for state in end_states]

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # overriding the default easing for the x property for each element
    elements = [
        VElement(
            renderer=renderer,
            keyframes=[(0, start_state), (0.1 * (i + 1), middle_state), (1, end_state)],
            easing={"x": Easing.linear},
        )
        for i, (start_state, middle_state, end_state) in enumerate(
            zip(start_states, middle_states, end_states)
        )
    ]

    # Add all elements to the scene
    scene.add_elements(elements)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to MP4 file
    exporter.to_mp4(
        filename="08_keyframes_variety.mp4",
        total_frames=90,
        framerate=30,
        width_px=512,
        num_thumbnails=20,
    )


if __name__ == "__main__":
    main()
