"""Element class - the central object that combines renderers and states"""

from __future__ import annotations
from typing import Optional, Dict, Callable, List, Union, Tuple

import drawsvg as dw

from vood.components.base import Renderer, State
from vood.velements.base_velement import BaseVElement


class VElement(BaseVElement):
    """Central object that combines a renderer with its state(s)

    Can be used for static rendering (single state) or animation (keyframes/states).
    This is the main object users work with.
    """

    def __init__(
        self,
        renderer: Renderer,
        state: Optional[State] = None,
        states: Optional[List[State]] = None,
        keyframes: Optional[List[Tuple[float, State]]] = None,
        easing: Optional[Dict[str, Callable[[float], float]]] = None,
    ) -> None:
        """Initialize an element

        Args:
            renderer: The renderer to render
            state: Single state for static element
            states: List of states for evenly-timed animation
            keyframes: List of (frame_time, state) tuples for precise timing
            easing: Optional dict to override default easing functions
        """
        self.renderer = renderer

        # Call parent constructor with keyframe parameters
        super().__init__(state=state, states=states, keyframes=keyframes, easing=easing)

    def render(self) -> dw.DrawingElement:
        """Render the element in its current state (static rendering)

        Returns:
            drawsvg element representing the element
        """
        return self.render_at_frame_time(0.0)

    def render_at_frame_time(self, t: float) -> dw.DrawingElement:
        """Render the element at a specific animation frame_time

        Args:
            t: frame_time factor from 0.0 to 1.0

        Returns:
            drawsvg element representing the element at frame_timeframe_time t
        """
        # Get the interpolated state at frame_time t
        interpolated_state = self._get_state_at_time(t)

        # Render the renderer with the interpolated state
        return self.renderer.render(interpolated_state)
