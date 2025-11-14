"""Element class - the central object that combines renderers and states"""

from __future__ import annotations
from typing import Any, Iterable, Optional, Dict, Callable, List, Union, Tuple

import drawsvg as dw

from vood.components import Renderer, State
from vood.velements.base_velement import (
    BaseVElement,
    SegmentKeystateTuple,
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
        renderer: Renderer,
        state: Optional[State] = None,
        # Updated keystates type
        keystates: Optional[Iterable[SegmentKeystateTuple]] = None,
        # NEW/Renamed: Instance-level easing override (Level 2)
        instance_easing: Optional[Dict[str, Callable[[float], float]]] = None,
        # NEW: Custom property timelines (Level 4 control)
        property_timelines: Optional[PropertyTimelineConfig] = None,
    ) -> None:

        self.renderer = renderer

        # Call parent constructor with keystate parameters
        super().__init__(
            state=state,
            keystates=keystates,
            instance_easing=instance_easing,
            property_timelines=property_timelines,
        )

    def render(self) -> Optional[dw.DrawingElement]:
        """Render the element in its current state (static rendering)

        Returns:
            drawsvg element representing the element, or None if element
            doesn't exist at t=0.0
        """
        return self.render_at_frame_time(0.0)

    def render_at_frame_time(self, t: float) -> Optional[dw.DrawingElement]:
        """Render the element at a specific animation frame_time

        Args:
            t: frame_time factor from 0.0 to 1.0

        Returns:
            drawsvg element representing the element at time t, or None if
            element doesn't exist at this time (outside keystate range)
        """
        # Get the interpolated state at frame_time t
        interpolated_state = self._get_state_at_time(t)

        # If no state (outside keystate range), don't render
        if interpolated_state is None:
            return None

        # Render the renderer with the interpolated state
        return self.renderer.render(interpolated_state)
