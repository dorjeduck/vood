from dataclasses import replace
from vood.component import TextRenderer, TextState
from vood.component.renderer.base_vertex import VertexRenderer
from vood.component.renderer.circle import CircleRenderer
from vood.component.renderer.perforated_primitive import PerforatedPrimitiveRenderer
from vood.component.renderer.ring import RingRenderer
from vood.component.state.circle import CircleState
from vood.component.state.perforated.base import Circle
from vood.component.state.perforated.circle import PerforatedCircleState
from vood.component.state.ring import RingState
from vood.converter.converter_type import ConverterType
from vood import layout
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color

configure_logging(level="INFO")

FILL_COLOR = Color("#FDBE02")
STROKE_COLOR = Color("#AA0000")


def main():

    # Create the scene
    scene = VScene(width=1024, height=512, background=Color("#000017"))

    # Create text states for each number with consistent styling

    s1 = PerforatedCircleState(
        radius=200,
        holes=[
            Circle(radius=100),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=6,
        holes_stroke_width=0,
        holes_fill_color=Color(255, 100, 255),
        holes_fill_opacity=0.4,
        x=-10,
    )

    s2 = replace(s1, x=10)

    states = [s1, s2]

    # Create a text renderer for all numbers

    # Create visual elements from states
    # VElements in Vood are the combination of one renderer and one or more states

    elements = [
        VElement(
            state=state,
        )
        for state in states
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
    exporter.export(
        filename="ring_experiment", formats=["svg", "png"], png_width_px=1024
    )


if __name__ == "__main__":
    main()
