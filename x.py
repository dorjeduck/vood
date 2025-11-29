from vood.component.state.polygon import PolygonState
from vood.component.state.triangle import TriangleState
from vood.core.color import Color
from vood.vscene import VScene
from vood.velement import VElement
from vood.component.state import CircleState


START_COLOR = Color("#FDBE02")
END_COLOR = Color("#AA0000")

ROTATION = 180. 

# Create animated scene
scene = VScene(width=400, height=400, background=Color("#000033"))
element = VElement(
    keystates=[
        (
            0,
            PolygonState(
                x=-80,
                y=-60,
                rotation=ROTATION,
                num_sides=5,
                size=50,
                fill_color=END_COLOR,
            ),
        ),
        (
            1,
            TriangleState(x=80, y=-60, size=50, fill_color=END_COLOR),
        ),
    ]
)
element2 = VElement(
    keystates=[
        (0, TriangleState(x=-80, y=60, size=50, fill_color=END_COLOR)),
        (
            1.0,
            TriangleState(x=80, y=60, rotation=ROTATION, size=50, fill_color=END_COLOR),
        ),
    ]
)
scene.add_element(element)
scene.add_element(element2)
