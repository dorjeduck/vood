from vood.components.text import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.state_functions import line_layout, wave_layout
from vood.utils.logger import configure_logging
from vood.velements import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter

configure_logging(level="INFO")


def main():

    ROUNDS = 10
    BASE_AMPLITUDE = 10

    # Create the scene
    scene = VScene(width=256, height=256, background="#000017")

    checkpoints = []

    # Create text states for each number with consistent styling
    base_states = [
        TextState(
            text=f"{num:02}",
            font_family="Courier",
            font_size=8,
            color="#FDBE02",
        )
        for num in range(1, 20)
    ]

    bases_states = line_layout(base_states, spacing=10)

    checkpoints.append(bases_states)

    checkpoints += [
        wave_layout(
            bases_states,
            spacing=10,
            wavelength=80,
            amplitude=(-1 if i % 2 else 1) * BASE_AMPLITUDE * (1 + 3 * i / ROUNDS),
        )
        for i in range(1, ROUNDS)
    ]

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    elements = [
        VElement(
            renderer=renderer,
            states=[*element_checkpoints],
        )
        for element_checkpoints in zip(*checkpoints)
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
        filename="06_the_wave.mp4",
        total_frames=30 * ROUNDS,
        framerate=30,
        width_px=512,
        num_thumbnails=10,
    )


if __name__ == "__main__":
    main()
