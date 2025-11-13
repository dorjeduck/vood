"""Element class - the central object that combines renderers and states"""

from __future__ import annotations
from typing import Any, Iterable, Optional, Dict, Callable, List, Union, Tuple

import drawsvg as dw

from vood.components import Renderer, State
from vood.velements.base_velement import BaseVElement


class VElement(BaseVElement):
    """Central object that combines a renderer with its state(s)

    Can be used for static rendering (single state) or animation (keyframes/states).
    This is the main object users work with.

    Elements only exist (render) within their keyframe time range. If keyframes
    don't cover the full [0, 1] timeline, the element won't render outside that range.
    """

    def __init__(
        self,
        renderer: Renderer,
        state: Optional[State] = None,
        states: Optional[Iterable[State]] = None,
        keyframes: Optional[Iterable[Tuple[float, State]]] = None,
        global_transitions: Optional[Dict[str, Tuple[Any, Any]]] = None,
        easing: Optional[Dict[str, Callable[[float], float]]] = None,
        segment_easing: Optional[Dict[int, Dict[str, Callable[[float], float]]]] = None,
    ) -> None:
        """Initialize an element

        Args:
            renderer: The renderer to render
            state: Single state for static element
            states: List of states for evenly-timed animation
            keyframes: List of (frame_time, state) tuples for precise timing.
                Element only exists between first and last keyframe times.
            global_transitions: Dict of property_name -> (start_value, end_value)
                for properties that should transition linearly across entire animation
                independent of keyframe structure
            easing: Optional dict to override default easing functions
            segment_easing: Optional dict of segment_index -> {property: easing_func}
        """
        self.renderer = renderer

        # Call parent constructor with keyframe parameters
        super().__init__(
            state=state,
            states=states,
            keyframes=keyframes,
            global_transitions=global_transitions,
            easing=easing,
            segment_easing=segment_easing,
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
            element doesn't exist at this time (outside keyframe range)
        """
        # Get the interpolated state at frame_time t
        interpolated_state = self._get_state_at_time(t)

        # If no state (outside keyframe range), don't render
        if interpolated_state is None:
            return None

        # Render the renderer with the interpolated state
        return self.renderer.render(interpolated_state)
