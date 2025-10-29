from vood.components.text import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.state_functions import circle_layout, grid_layout, line_layout
from vood.state_functions.enums import ElementAlignment
from vood.utils.logger import configure_logging
from vood.velements import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter

configure_logging(level="INFO")


def main():

    # Create the scene
    scene = VScene(width=256, height=256, background="#000017")

    # Create text states for each number with consistent styling
    start_states = [
        TextState(
            text=str(num),
            font_family="Courier",
            font_size=20,
            color="#FDBE02",
        )
        for num in range(1, 10)
    ]

    # grid and circle layout for the transition
    middle_states = grid_layout(start_states, cols=3, spacing_h=20, spacing_v=20)
    end_states = circle_layout(
        start_states, radius=80, alignment=ElementAlignment.LAYOUT
    )

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # Create visual elements from states
    # VElements in Vood are the combination of one renderer and one or more states
    elements = [
        VElement(
            renderer=renderer,
            states=[start_state, middle_state, end_state],
        )
        for start_state, middle_state, end_state in zip(
            start_states, middle_states, end_states
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
        filename="05_two_step_transition.mp4",
        total_frames=90,
        framerate=30,
        width_px=512,
        num_thumbnails=20,
    )


if __name__ == "__main__":
    main()
