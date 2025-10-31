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

START_COLOR = "#FDBE02"
END_COLOR = "#AA0000"


def main():

    # Create the scene
    scene = VScene(width=256, height=256, background="#000017")

    # Create text states for each number with consistent styling
    states = [
        TextState(
            text=str(num),
            font_family="Courier",
            font_size=20,
        )
        for num in range(1, 10)
    ]

    x_shifts = [-100, -40, 40, 100]

    all_states = [
        line_layout(states, center_x=x_shift, spacing=20, rotation=90)
        for x_shift in x_shifts
    ]

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # overriding the default easing for the x property for each element
    elements = [
        VElement(
            renderer=renderer,
            keyframes=[
                (0, state_a),
                (0.25, state_b),
                (0.5, state_b if i % 2 == 0 else state_c),
                (0.75, state_c),
                (1, state_d),
            ],
            easing={"x": Easing.linear},
            global_transitions={"color": (START_COLOR, END_COLOR)},
        )
        for i, (state_a, state_b, state_c, state_d) in enumerate(zip(*all_states))
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
        filename="12_give_me_a_break.mp4",
        total_frames=90,
        framerate=30,
        width_px=512,
        num_thumbnails=20,
    )


if __name__ == "__main__":
    main()
