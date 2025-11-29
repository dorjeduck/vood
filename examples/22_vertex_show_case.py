"""
Comprehensive showcase of all vood layout functions
Demonstrates each layout's unique characteristics with animated transitions
"""

from vood.component import TextRenderer, TextState, Renderer
from vood.converter.converter_type import ConverterType
from vood.component.state import (
    ArcState,
    ArrowState,
    CircleState,
    CrossState,
    EllipseState,
    FlowerState,
    HeartState,
    InfinityState,
    LineState,
    PolygonState,
    RectangleState,
    SpiralState,
    SquareState,
    StarState,
    TriangleState,
    WaveState,
)
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from dataclasses import replace
from vood.core.color import Color

from vood.animation.atomic import sequential_transition, fade, trim

configure_logging(level="INFO")

FILL_COLOR = Color("#FDBE02")
STROKE_COLOR = Color("#AA0000")


def main():
    # Create the scene
    scene = VScene(width=256, height=256, background=Color("#000017"))

    base_name_state = TextState(
        text="",
        font_family="Courier New",
        font_size=20,
        fill_color=Color("#AA0000"),
        y=110,
    )

    # Define all layout transitions
    vertex_states = []
    vertex_name_states = []

    vertex_states.append(CircleState(fill_color=FILL_COLOR, stroke_color=STROKE_COLOR))
    vertex_name_states.append(replace(base_name_state, text="Circle"))
    
    vertex_states.append(
        ArrowState(fill_color=FILL_COLOR, stroke_color=STROKE_COLOR, rotation=-45)
    )
    vertex_name_states.append(replace(base_name_state, text="Arrow"))
    
    vertex_states.append(
        CrossState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Cross"))
    
    vertex_states.append(
        LineState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Line"))

    vertex_states.append(
        EllipseState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Ellipse"))

    vertex_states.append(
        PolygonState(fill_color=FILL_COLOR, stroke_color=STROKE_COLOR, num_sides=5)
    )
    vertex_name_states.append(replace(base_name_state, text="Pentagon"))
    
    vertex_states.append(FlowerState(fill_color=FILL_COLOR, stroke_color=STROKE_COLOR))
    vertex_name_states.append(replace(base_name_state, text="Flower"))

    vertex_states.append(
        HeartState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Heart"))
    
    vertex_states.append(
        WaveState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Wave"))

    vertex_states.append(
        PolygonState(fill_color=FILL_COLOR, stroke_color=STROKE_COLOR, num_sides=6)
    )
    vertex_name_states.append(replace(base_name_state, text="Hexagon"))

    vertex_states.append(
        InfinityState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Infinity"))

    vertex_states.append(
        PolygonState(fill_color=FILL_COLOR, stroke_color=STROKE_COLOR, num_sides=8)
    )

    vertex_name_states.append(replace(base_name_state, text="Octagon"))

    vertex_states.append(
        ArcState(
            stroke_color=STROKE_COLOR,
            radius=40,
            start_angle=10,
            end_angle=170,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Arc"))

    vertex_states.append(
        RectangleState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    
    vertex_name_states.append(replace(base_name_state, text="Rectangle"))
    
    vertex_states.append(
        PolygonState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    
    vertex_name_states.append(replace(base_name_state, text="Polygon"))
    
    vertex_states.append(
        SpiralState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Spiral"))
    
    vertex_states.append(
        SquareState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Square"))

    vertex_states.append(
        StarState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Star"))

    vertex_states.append(
        TriangleState(
            fill_color=FILL_COLOR,
            stroke_color=STROKE_COLOR,
        )
    )
    vertex_name_states.append(replace(base_name_state, text="Triangle"))
    

    # pause morph shapes for a short time

    vertex_keystates = sequential_transition(vertex_states, trim, 0.8)

    # Add all elements to the scene
    scene.add_element(
        VElement(
            keystates=vertex_keystates,
        )
    )
   

    text_keyframes = sequential_transition(vertex_name_states, fade, 0.5)

    texts = VElement(renderer=TextRenderer(), keystates=text_keyframes)
    scene.add_element(texts)
   
    # Create the exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.CAIROSVG,
        output_dir="output/",
    )

    # Export to MP4 file
    exporter.to_mp4(
        filename="22_vertex_showcase.mp4",
        total_frames=len(vertex_states) * 30,
        framerate=30,
        png_width_px=1024,
    )


if __name__ == "__main__":
    main()
