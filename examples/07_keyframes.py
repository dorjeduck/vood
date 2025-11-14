from vood.components import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.magic import layouts
from vood.core.logger import configure_logging
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
            text=f"{num:02}",
            font_family="Courier New",
            font_size=8,
            color="#FDBE02",
        )
        for num in range(1, 20)
    ]

    # Arrange the numbers in a circular layout for the middle states
    middle_states = layouts.circle(
        start_states,
        radius=96,
        alignment=layouts.ElementAlignment.LAYOUT,
    )

    end_states = layouts.spiral(
        start_states,
        radius_step=3,
        angle_step=30,
        alignment=layouts.ElementAlignment.LAYOUT,
    )

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # keyframe fine tuning, 4 times faster between start and middle than middle to end

    elements = [
        VElement(
            renderer=renderer,
            keyframes=[(0, start_state), (0.2, middle_state), (1, end_state)],
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

    # Export to mp4
    exporter.to_mp4(
        filename="07_key_frames",
        total_frames=90,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
