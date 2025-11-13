from vood import animation
from vood.transition import easing
from vood.component import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
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
    states = [
        TextState(
            text=text,
            font_family="Courier New",
            font_size=42,
        )
        for text in ["Empty", "Mirror"]
    ]

    fade_keyframes = animation.compound.slide_replace(
        state1=states[0],
        state2=states[1],
        at_time=0.5,
        duration=0.4,
        distance=100,
        direction=animation.compound.SlideDirection.UP,
        extend_timeline=True,
    )

    renderer = TextRenderer()

    opacity_easing = (easing.in_cubic, easing.out_cubic)

    elements = [
        VElement(
            renderer=renderer,
            keystates=keystates,
            property_keystates={"fill_color": [START_COLOR, END_COLOR]},
            property_easing={"opacity": opacity_easing[i]},
        )
        for i, keystates in enumerate(fade_keyframes)
    ]

    scene.add_elements(elements)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to mp4
    exporter.to_mp4(
        filename="17_compound_animation",
        total_frames=150,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
