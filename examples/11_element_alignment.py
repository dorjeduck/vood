from vood.components.text import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.state_functions import ellipse_layout
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
    # These states will be the starting point of the animation
    start_states = [
        TextState(
            x=0,  # centered horizontally (default but explicit for clarity)
            y=0,  # centered vertically (...)
            text=str(num),
            font_family="Courier",
            font_size=20,
            color="#FDBE02",
        )
        for num in range(1, 10)
    ]

    start_states = ellipse_layout(
        start_states,
        radius_x=96,
        radius_y=64,
        rotation=0,
        alignment=ElementAlignment.LAYOUT,
    )

    end_states = ellipse_layout(
        start_states,
        radius_x=96,
        radius_y=64,
        rotation=0,
        alignment=ElementAlignment.UPRIGHT,
    )

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # Create visual elements from states by
    # pairing each start state with its corresponding end state
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
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to mp4
    exporter.to_mp4(
        filename="11_element_alignment",
        total_frames=20,
        framerate=10,
        width_px=512,
    )


if __name__ == "__main__":
    main()
