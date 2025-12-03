"""State for collections of shapes that morph M→N"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List

from vood.component.state.base import State
from vood.component.registry import renderer
from vood.transition import easing


# Forward reference - actual import happens in renderer module
def _get_renderer():
    from vood.component.renderer.shape_collection import ShapeCollectionRenderer
    return ShapeCollectionRenderer


@renderer(_get_renderer)
@dataclass(frozen=True)
class ShapeCollectionState(State):
    """State containing a collection of shapes that can morph M→N

    This enables general M→N shape morphing where multiple independent
    shapes can smoothly transition to a different number of shapes.

    Example:
        # 3 shapes → 2 shapes morphing
        state1 = ShapeCollectionState(shapes=[
            CircleState(x=-50, radius=30),
            RectangleState(x=0, width=40, height=40),
            CircleState(x=50, radius=30)
        ])
        state2 = ShapeCollectionState(shapes=[
            EllipseState(x=-40, rx=50, ry=30),
            EllipseState(x=40, rx=50, ry=30)
        ])

        elem = VElement(keystates=[state1, state2])
    """

    shapes: Optional[List[State]] = None

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "shapes": easing.linear,
    }
