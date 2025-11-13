from vood.components import TextRenderer, TextState
from vood.converter.converter_type import ConverterType
from vood.magic import layouts
from vood.utils.logger import configure_logging
from vood.velements import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter

configure_logging(level="DEBUG")


def main():

    # Create the scene
    scene = VScene(width=256, height=256, background="#000017")

    # Create text states for each number with consistent styling
    base_name_state = TextState(
        text="Fun Grid",
        font_family="Courier New",
        font_size=20,
        color="#AA0000",
        y=110,
    )

    # Create a text renderer for all numbers
    renderer = TextRenderer()

    # Create visual elements from states
    # VElements in Vood are the combination of one renderer and one or more states

    telement = VElement(renderer=renderer, state=base_name_state)

    # Add all elements to the scene
    scene.add_element(telement)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to PNG file
    exporter.export(filename="x", formats=["svg", "png"], png_width_px=1024)


if __name__ == "__main__":
    main()
