"""Element class - the central object that combines renderers and states"""

from __future__ import annotations
from typing import Any, Iterable, Optional, Dict, Callable, List, Union, Tuple

import drawsvg as dw

from vood.component import Renderer, State
from vood.velement.base_velement import BaseVElement
from vood.velement.keystate_parser import (
    FlexibleKeystateInput,
    PropertyTimelineConfig,
)


class VElement(BaseVElement):
    """Central object that combines a renderer with its state(s)

    Can be used for static rendering (single state) or animation (keystates/states).
    This is the main object users work with.

    Elements only exist (render) within their keystate time range. If keystates
    don't cover the full [0, 1] timeline, the element won't render outside that range.
    """

    def __init__(
        self,
        renderer: Optional[Renderer] = None,
        state: Optional[State] = None,
        # Flexible keystates: accepts tuples, bare states, or KeyState objects
        keystates: Optional[Iterable[FlexibleKeystateInput]] = None,
        # NEW/Renamed: Instance-level easing override (Level 2)
        property_easing: Optional[Dict[str, Callable[[float], float]]] = None,
        # NEW: Custom property timelines (Level 4 control)
        property_keystates: Optional[PropertyTimelineConfig] = None,
    ) -> None:

        self.renderer = renderer

        # Call parent constructor with keystate parameters
        super().__init__(
            state=state,
            keystates=keystates,
            property_easing=property_easing,
            property_keystates=property_keystates,
        )

    def render(self) -> Optional[dw.DrawingElement]:
        """Render the element in its current state (static rendering)

        Returns:
            drawsvg element representing the element, or None if element
            doesn't exist at t=0.0
        """
        return self.render_at_frame_time(0.0)

    def render_at_frame_time(
        self, t: float, drawing: Optional[dw.Drawing] = None
    ) -> Optional[dw.DrawingElement]:
        """Render the element at a specific animation frame_time

        Args:
            t: frame_time factor from 0.0 to 1.0
            drawing: Optional Drawing object for accessing defs section

        Returns:
            drawsvg element representing the element at time t, or None if
            element doesn't exist at this time (outside keystate range)
        """
        # Get the interpolated state at frame_time t
        interpolated_state, inbetween = self._get_state_at_time(t)

        # If no state (outside keystate range), don't render
        if interpolated_state is None:
            return None

        if inbetween:
            renderer = interpolated_state.get_vertex_renderer_class()()
        else:
            renderer = (
                self.renderer
                if self.renderer
                else interpolated_state.get_renderer_class()()
            )
   
        return renderer.render(interpolated_state, drawing=drawing)
