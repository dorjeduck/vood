from dataclasses import replace

from vood.component import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood import layout
from vood.transition import easing
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.velement.velement_group import VElementGroup, VElementGroupState
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

    x_shifts = [-100, 60]

    all_states = [
        layout.line(states, cx=x_shift, spacing=20, rotation=90) for x_shift in x_shifts
    ]

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # overriding the default easing for the x property for each element
    elements = [
        VElement(
            renderer=renderer,
            keystates=states,
            property_easing={"x": easing.linear},
            property_keystates={"fill_color": [START_COLOR, END_COLOR]},
        )
        for states in zip(*all_states)
    ]

    g_start_state = VElementGroupState()

    g1_end_state = VElementGroupState(rotation=75, transform_origin_x=x_shifts[1] / 2)
    g2_end_state = VElementGroupState(rotation=-75, transform_origin_x=x_shifts[1] / 2)

    g1 = VElementGroup(
        elements=elements[:4],
        keystates=[
            (0, g_start_state),
            (0.5, g_start_state),
            (1, g1_end_state),
        ],
    )
    g2 = VElementGroup(
        elements=elements[5:],
        keystates=[
            (0, g_start_state),
            (0.5, g_start_state),
            (1, g2_end_state),
        ],
    )
    scene.add_elements([g1, g2])

    # adding the middle element as it is not part of any group
    scene.add_element(elements[4])

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to MP4 file
    exporter.to_mp4(
        filename="15_group_dynamics",
        total_frames=90,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
