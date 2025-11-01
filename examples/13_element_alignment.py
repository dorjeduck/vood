from vood.components.text import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.state_functions import circle_layout
from vood.state_functions.enums import ElementAlignment
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
    # These states will be the starting point of the animation
    base_states = [
        TextState(
            text=f"{num:02}",
            font_family="Courier",
            font_size=20,
            color="#FDBE02",
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
        circle_layout(base_states, radius=100, alignment=ElementAlignment.UPRIGHT),
        circle_layout(base_states, radius=100, alignment=ElementAlignment.LAYOUT),
        circle_layout(
            base_states,
            radius=100,
            alignment=ElementAlignment.LAYOUT,
            element_rotation_offset=90,
        ),
        circle_layout(
            base_states,
            radius=100,
            alignment=ElementAlignment.LAYOUT,
            element_rotation_offset_fn=east_west,
        ),
    ]

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # Create visual elements

    elements = [
        VElement(
            renderer=renderer,
            keyframes=[(i / 7, [a, b, c, d][i // 2]) for i in range(8)],
            global_transitions={"color": (START_COLOR, END_COLOR)},
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
        filename="13_element_alignment",
        total_frames=120,
        framerate=30,
        width_px=512,
        num_thumbnails=20,
    )


if __name__ == "__main__":
    main()
