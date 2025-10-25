from vood.components.text import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.state_functions import ellipse_layout
from vood.utils.logger import configure_logging
from vood.velements import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter

configure_logging(level="INFO")


def main():

    # Create the scene
    scene = VScene(width=256, height=192, background="#000017")

    # Create text states for each number with consistent styling
    states = [
        TextState(
            text=str(num),
            font_family="Courier",
            font_size=20,
            color="#FDBE02",
        )
        for num in range(1, 10)
    ]

    # Arrange the numbers in an elliptical layout
    states_layout = ellipse_layout(
        states,
        radius_x=96,
        radius_y=64,
    )

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # Create visual elements from states
    # VElements in Vood are the combination of one renderer and one or more states
    elements = [
        VElement(
            renderer=renderer,
            state=state,
        )
        for state in states_layout
    ]

    # Add all elements to the scene
    scene.add_elements(elements)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to PNG file
    exporter.to_png(filename="01_ellipse_layout.png", width_px=512)


if __name__ == "__main__":
    main()
