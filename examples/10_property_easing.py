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


def main():

    # Create the scene
    scene = VScene(width=256, height=256, background=Color("#000017"))

    # Create text states for each number with consistent styling
    states = [
        TextState(
            text=str(num),
            font_family="Courier New",
            font_size=20,
            fill_color=Color("#FDBE02"),
        )
        for num in range(1, 10)
    ]

    # Arrange the numbers along a line for start and end positions
    start_states = layout.line(states, center_x=-100, spacing=20, rotation=90)
    end_states = layout.line(states, center_x=100, spacing=20, rotation=90)

    # lets animate also a change of color
    end_states = [replace(state, fill_color=Color("#AA0000")) for state in end_states]

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    easing_overrides = [
        easing.linear,
        easing.in_out,
        easing.in_out_bounce,
        easing.in_bounce,
        easing.out_bounce,
        easing.in_out_quad,
        easing.out_quad,
        easing.in_out_cubic,
        easing.out_cubic,
    ]

    # overriding the default easing for the x property for each element
    elements = [
        VElement(
            renderer=renderer,
            keystates=[start_state, end_state],
            property_easing={"x": easing},
        )
        for start_state, end_state, easing in zip(
            start_states, end_states, easing_overrides
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
        filename="10_instance_easing",
        total_frames=90,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
