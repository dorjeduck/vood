from dataclasses import replace
from vood.component.state.line import LineState
from vood.component.state.polygon import PolygonState
from vood.component.state.triangle import TriangleState
from vood.core.color import Color
from vood.vscene import VScene
from vood.velement import VElement
from vood.component.state import CircleState


START_COLOR = Color("#FDBE02")
MIDDLE_COLOR = Color("#55aa22")
END_COLOR = Color("#AA0000")

# Create animated scene
scene = VScene(width=400, height=400, background=Color("#000033"))

s1 = LineState(length=100, stroke_color=START_COLOR, stroke_width=10)
s2 = CircleState(radius=100, stroke_color=MIDDLE_COLOR)
s3 = replace(s1, rotation=90, stroke_color=END_COLOR)

element = VElement(keystates=[s1, s2, s3])

scene.add_element(element)
