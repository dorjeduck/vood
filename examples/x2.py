from vood.component.renderer.base_morph import MorphRenderer
from vood.component.renderer.arrow import ArrowRenderer
from vood.component.renderer.path import PathRenderer
from vood.component.state.arrow import ArrowState
from vood.component.state.path import MorphMethod, PathState
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

    state = RingState(
        inner_radius=30,
        outer_radius=50
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
        converter=ConverterType.CAIROSVG,
        output_dir="output/",
    )

    # Export to PNG file
    exporter.export(filename="x2", formats=["svg", "png"], png_width_px=1024)


if __name__ == "__main__":
    main()
