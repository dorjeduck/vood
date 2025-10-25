from dataclasses import dataclass, replace
import drawsvg as dw
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vood.transitions.easing import Easing
from vood.components import Renderer, CircleRenderer, CircleState


@dataclass
class DoubleCircleState(CircleState):
    distance: float = 0  # Distance between the two circles
  

    DEFAULT_EASING = {
        **CircleState.DEFAULT_EASING,
        "distance": Easing.in_out,

    }


class DoubleCircleRenderer(Renderer):
    circle_one: CircleRenderer
    circle_two: CircleRenderer

    def __init__(self) -> None:
        """Initialize circle renderer

        No parameters needed - all properties come from the state
        """
        self.circle_one = CircleRenderer()
        self.circle_two = CircleRenderer()

    def _render_core(self, state: DoubleCircleState) -> dw.Group:
        state1, state2 = self._get_states(state)
        group = dw.Group()
        group.append(self.circle_one.render(state1))
        group.append(self.circle_two.render(state2))
        return group

    def _get_states(self, state):

        state1 = replace(
            state,
            x=-state.radius - state.distance / 2,
            y=0,
        )
        state2 = replace(
            state,
            x=state.radius + state.distance / 2,
            y=0,
        )
        return state1, state2
