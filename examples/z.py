from vood.component.state.ring import RingState
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color

configure_logging(level="INFO")


def main():

    START_COLOR = Color("#FDBE02")
    END_COLOR = Color("#AA0000")

    # Create the scene
    scene = VScene(width=256, height=256, background=Color("#000017"))

    # Create text states for each number with consistent styling

    state = RingState(
        x=0,  # Center of the scene
        y=0,  # Center of the scene
        inner_radius=100,
        outer_radius=120,
        fill_color=END_COLOR,
        stroke_color=START_COLOR,
        stroke_width=10,
    )

    # Create visual elements from states
    # VElements in Vood are the combination of one renderer and one or more states

    element = VElement(
        state=state,
    )

    # Add all elements to the scene
    scene.add_element(element)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.INKSCAPE,
        output_dir="output/",
    )

    # Export to PNG file
    exporter.export(filename="z", formats=["svg", "png"], png_width_px=1024)


if __name__ == "__main__":
    main()
