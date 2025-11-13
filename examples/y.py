from vood.component.renderer.base_vertex import VertexRenderer
from vood.component.state.perforated_shape import PerforatedShapeState
from vood.component.state.poly_ring import PolyRingState
from vood.component.state.ring import RingState
from vood.component.state.square import SquareState
from vood.component.state.square_ring import SquareRingState
from vood.component.state.triangle import TriangleState
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color
from dataclasses import replace

configure_logging(level="INFO")

FILL_COLOR = Color("#ff0000")
STROKE_COLOR = Color("#ffffff")


def main():

    # Create the scene
    scene = VScene(width=1024, height=1024, background=Color("#000017"))

    state1 = RingState(
        fill_color=FILL_COLOR,
        stroke_color=STROKE_COLOR,
        inner_radius=100,
        outer_radius=200,
        stroke_width=4,
    )

    state2 = PerforatedShapeState(
        x=-300,
        y=-300,
        outer_shape={"type": "circle", "radius": 150},
        holes=[
            {
                "type": "astroid",
                "radius": 35,
                "num_cusps": 4,
                "curvature": 0.3,
                "x": -70,
                "y": -70,
            },
            
           
            {
                "type": "astroid",
                "radius": 35,
                "num_cusps": 4,
                "curvature": 0.9,
                "x": 70,
                "y": 70,
            },
        ],
        fill_color=Color("#AA96DA"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    state3 = PerforatedShapeState(
        x=300, y=300,
        outer_shape={"type": "astroid", "radius": 120, "num_cusps": 8, "curvature": 0.65},
        holes=[
            {"type": "circle", "radius": 15, "x": 0, "y": 0},
            {"type": "astroid", "radius": 18, "num_cusps": 3, "curvature": 0.8, "x": -50, "y": 0, "rotation": 30},
            {"type": "astroid", "radius": 18, "num_cusps": 3, "curvature": 0.8, "x": 50, "y": 0, "rotation": 30},
            {"type": "square", "size": 20, "x": 0, "y": -50, "rotation": 45},
            {"type": "square", "size": 20, "x": 0, "y": 50, "rotation": 45},
        ],
        fill_color=Color("#95E1D3"),
        stroke_color=Color("#FFFFFF"),
        stroke_width=2,
    )

    element = VElement(
        renderer=VertexRenderer(),
        keystates=[
            (0, state3),
            (1, state2),
            #(1, state3),
        ],
    )

    scene.add_element(element)

    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.INKSCAPE,
        output_dir="output/",
    )

    # Export to PNG file
    exporter.to_mp4(
        filename="y.mp4",
        total_frames=60,
        framerate=15,
        png_width_px=512,
    )


if __name__ == "__main__":
    main()
