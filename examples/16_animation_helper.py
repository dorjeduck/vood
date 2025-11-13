from vood.magic import animations
from vood.components import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
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
    states = [
        TextState(
            text=text,
            font_family="Courier New",
            font_size=42,
        )
        for text in ["Empty", "Mirror"]
    ]

    fade_keyframes = animations.atomic.fade(
        states[0], states[1], at_time=0.5, duration=0.4, extend_timeline=True
    )

    renderer = TextRenderer()

    element = VElement(
        renderer=renderer,
        keyframes=fade_keyframes,
        global_transitions={"color": (START_COLOR, END_COLOR)},
    )

    scene.add_element(element)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to mp4
    exporter.to_mp4(
        filename="16_animation_helper",
        total_frames=150,
        framerate=30,
        width_px=1024,
    )


if __name__ == "__main__":
    main()
