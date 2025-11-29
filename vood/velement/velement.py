"""Element class - the central object that combines renderers and states"""

from __future__ import annotations
from typing import Any, Iterable, Optional, Dict, Callable, List, Union, Tuple

import drawsvg as dw

from vood.component import Renderer, State, get_renderer_instance_for_state
from vood.velement.base_velement import BaseVElement
from vood.component.renderer.base_vertex import VertexRenderer
from vood.velement.keystate_parser import (
    FlexibleKeystateInput,
    PropertyKeyStatesConfig,
)
from vood.core.point2d import Point2D, Points2D


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
        property_keystates: Optional[PropertyKeyStatesConfig] = None,
    ) -> None:

        self.renderer = renderer

        # Vertex buffer cache for optimized interpolation
        # Cache keyed by (num_vertices, num_holes) to reuse buffers across frames
        self._vertex_buffer_cache: Dict[Tuple[int, int], Tuple[Points2D, List[Points2D]]] = {}

        # Call parent constructor with keystate parameters
        super().__init__(
            state=state,
            keystates=keystates,
            property_easing=property_easing,
            property_keystates=property_keystates,
        )

    def get_frame(self, t: float) -> Optional[State]:
        """Get the interpolated state at a specific time

        Args:
            t: Time factor from 0.0 to 1.0

        Returns:
            Interpolated state at time t, or None if element doesn't exist at this time
        """
        state, _ = self._get_state_at_time(t)
        return state

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
            
            #renderer_class = interpolated_state.get_vertex_renderer_class()
            renderer = VertexRenderer()
        else:
            if self.renderer:
                renderer = self.renderer
            else:
                
                renderer = get_renderer_instance_for_state(interpolated_state)
                

        return renderer.render(interpolated_state, drawing=drawing)

    def _get_vertex_buffer(self, num_verts: int, num_holes: int) -> Tuple[Points2D, List[Points2D]]:
        """Get or create reusable vertex buffer for interpolation

        Buffers are cached to avoid creating new Point2D lists for every frame.
        Each buffer is sized for a specific (num_vertices, num_holes) combination.

        Args:
            num_verts: Number of vertices in the outer contour
            num_holes: Number of holes in the shape

        Returns:
            Tuple of (outer_buffer, hole_buffers) where:
            - outer_buffer: List of Point2D for outer contour
            - hole_buffers: List of Lists of Point2D, one per hole
        """
        key = (num_verts, num_holes)
        if key not in self._vertex_buffer_cache:
            # Create new buffer with pre-allocated Point2D objects
            outer_buffer = [Point2D(0.0, 0.0) for _ in range(num_verts)]
            hole_buffers = [[Point2D(0.0, 0.0) for _ in range(num_verts)] for _ in range(num_holes)]
            self._vertex_buffer_cache[key] = (outer_buffer, hole_buffers)

        return self._vertex_buffer_cache[key]

