from vood.component import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood import layout
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color

configure_logging(level="INFO")


def main():

    ROUNDS = 10
    BASE_AMPLITUDE = 10

    # Create the scene
    scene = VScene(width=256, height=256, background=Color("#000017"))

    checkpoints = []

    # Create text states for each number with consistent styling
    base_states = [
        TextState(
            text=f"{num:02}",
            font_family="Courier New",
            font_size=8,
            fill_color=Color("#FDBE02"),
        )
        for num in range(1, 20)
    ]

    bases_states = layout.line(base_states, spacing=10)

    checkpoints.append(bases_states)

    checkpoints += [
        layout.wave(
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
            keystates=states,
        )
        for states in zip(*checkpoints)
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
        filename="06_the_wave",
        total_frames=30 * ROUNDS,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
