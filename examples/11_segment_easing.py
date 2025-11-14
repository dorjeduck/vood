from vood.components import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.magic import layouts
from vood.transitions import easing
from vood.core.logger import configure_logging
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
            font_family="Courier New",
            font_size=20,
        )
        for num in range(1, 10)
    ]

    x_shifts = [-100, -50, 50, 100]

    all_states = [
        layouts.line(states, center_x=x_shift, spacing=20, rotation=90)
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
                (0.75, state_c),
                (1, state_d),
            ],
            easing={"x": easing.linear},
            segment_easing={
                1: {"x": easing.in_out_sine if i % 2 == 1 else easing.linear}
            },
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
        filename="11_segment_easing",
        total_frames=90,
        framerate=30,
        width_px=1024,
    )


if __name__ == "__main__":
    main()
