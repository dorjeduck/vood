from vood.component import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood import layout
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
    # These states will be the starting point of the animation
    base_states = [
        TextState(
            text=f"{num:02}",
            font_family="Courier New",
            font_size=20,
            fill_color=Color("#FDBE02"),
        )
        for num in range(1, 20)
    ]

    def east_west(angle):
        if angle == 0:
            return 0
        elif angle > 180:
            return 90
        else:
            return -90

    all_states = [
        layout.circle(
            base_states, radius=100, alignment=layout.ElementAlignment.UPRIGHT
        ),
        layout.circle(
            base_states, radius=100, alignment=layout.ElementAlignment.LAYOUT
        ),
        layout.circle(
            base_states,
            radius=100,
            alignment=layout.ElementAlignment.LAYOUT,
            element_rotation_offset=90,
        ),
        layout.circle(
            base_states,
            radius=100,
            alignment=layout.ElementAlignment.LAYOUT,
            element_rotation_offset_fn=east_west,
        ),
    ]

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # Create visual elements

    elements = [
        VElement(
            renderer=renderer,
            keystates=[(i / 7, [a, b, c, d][i // 2]) for i in range(8)],
            property_keystates={"fill_color": [START_COLOR, END_COLOR]},
        )
        for a, b, c, d in zip(*all_states)
    ]

    # Add all elements to the scene
    scene.add_elements(elements)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to mp4
    exporter.to_mp4(
        filename="14_element_alignment",
        total_frames=210,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
