from dataclasses import replace

from vood.component import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood import layout
from vood.transition import easing
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color

configure_logging(level="INFO")

START_COLOR = Color("#FDBE02")
END_COLOR = Color("#AA0000")


def main():

    # Create the scene
    scene = VScene(width=256, height=256, background=Color("#000017"))

    # Create text states for each number with consistent styling
    states = [
        TextState(
            text=str(num),
            font_family="Courier New",
            font_size=20,
        )
        for num in range(1, 10)
    ]

    x_shifts = [-100, 100]

    all_states = [
        layout.line(states, cx=x_shift, spacing=20, rotation=90) for x_shift in x_shifts
    ]

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # overriding the default easing for the x property for each element
    elements = [
        VElement(
            renderer=renderer,
            keystates=[
                (0.3 if i % 2 else 0, state_a),
                (0.7 if i % 2 else 1, state_b),
            ],
            property_easing={"x": easing.linear},
            property_keystates={"fill_color": [START_COLOR, END_COLOR]},
        )
        for i, (state_a, state_b) in enumerate(zip(*all_states))
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
        filename="13_not_always",
        total_frames=90,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
