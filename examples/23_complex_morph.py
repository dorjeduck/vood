from vood.animation.atomic import sequential_transition, trim
from vood.component.renderer.base_vertex import VertexRenderer
from vood.component.state import (
    PerforatedCircleState,
    PerforatedStarState,
    Astroid,
    Star,
    Ellipse,
    Polygon,
    Circle,
)
from vood.component.state.ring import RingState

from vood.converter.converter_type import ConverterType
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
    scene = VScene(width=1024, height=1024, background=Color("#000017"))

    # equivalent to a Ring but the stroke around the hole which is present here
    # can smoothly morph into holes without surrounding strokes
    s1 = PerforatedCircleState(
        radius=200,
        holes=[Circle(radius=100)],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=6,
    )

    s2 = PerforatedCircleState(
        radius=270,
        holes=[
            Circle(radius=50, y=-100),
            Star(num_points=5, inner_radius=40, outer_radius=70, x=-120, y=60),
            Astroid(radius=100, num_cusps=4, curvature=0.3, x=100, y=60),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=6,
        holes_stroke_width=0,
    )

    s3 = PerforatedStarState(
        num_points=5,
        outer_radius=400,
        inner_radius=200,
        holes=[
            Ellipse(rx=50, ry=40, x=-70, y=-80),
            Polygon(num_sides=3, radius=80, x=40, y=40),
        ],
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=6,
        holes_stroke_width=0,
    )
    states = [s1, s2, s3, s2, s1]

    keystates = sequential_transition(states, trim, 0.5)

    element = VElement(renderer=VertexRenderer(), keystates=keystates)

    scene.add_element(element)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    # Export to PNG file
    exporter.to_mp4(
        filename="23_complex_morph.mp4",
        total_frames=240,
        framerate=30,
        png_width_px=1024,
        num_thumbnails=100,
    )


if __name__ == "__main__":
    main()
