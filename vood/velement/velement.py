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
        # NEW: VElement-based clipping/masking
        clip_element: Optional[VElement] = None,
        mask_element: Optional[VElement] = None,
        clip_elements: Optional[List[VElement]] = None,
    ) -> None:

        self.renderer = renderer

        # VElement-based clipping/masking
        self.clip_element = clip_element
        self.mask_element = mask_element
        self.clip_elements = clip_elements or []

        # Vertex buffer cache for optimized interpolation
        # Cache keyed by (num_vertices, num_vertex_loops ) to reuse buffers across frames
        self._vertex_buffer_cache: Dict[
            Tuple[int, int], Tuple[Points2D, List[Points2D]]
        ] = {}

        # Shape list matching cache for multi-shape morphing
        # Cache keyed by (field_name, segment_idx) to reuse M→N matching across frames
        self._shape_list_cache: Dict[
            Tuple[str, int], Tuple[List[State], List[State]]
        ] = {}

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

        # Apply VElement-based clips
        if self.clip_element or self.mask_element or self.clip_elements:

            interpolated_state = self._apply_velement_clips(interpolated_state, t)

        if inbetween:

            # renderer_class = interpolated_state.get_vertex_renderer_class()
            renderer = VertexRenderer()
        else:
            if self.renderer:
                renderer = self.renderer
            else:

                renderer = get_renderer_instance_for_state(interpolated_state)

        return renderer.render(interpolated_state, drawing=drawing)

    def _apply_velement_clips(self, state: State, t: float) -> State:
        """Inject VElement-based clips into state

        Renders clip VElements at time t and creates temporary states
        to inject into the main state's clip_state/mask_state fields.

        Args:
            state: Base state from keystate interpolation
            t: Current animation time

        Returns:
            State with clip_state/mask_state fields populated
        """
        from dataclasses import replace

        # Get clip states at time t
        mask_state_at_t = self.mask_element.get_frame(t) if self.mask_element else None
        clip_state_at_t = self.clip_element.get_frame(t) if self.clip_element else None
        clip_states_at_t = None

        if self.clip_elements:
            clip_states_at_t = [
                elem.get_frame(t)
                for elem in self.clip_elements
                if elem.get_frame(t) is not None
            ]

        # Inject into state
        return replace(
            state,
            clip_state=clip_state_at_t or state.clip_state,
            mask_state=mask_state_at_t or state.mask_state,
            clip_states=clip_states_at_t or state.clip_states,
        )

    def _get_vertex_buffer(
        self, num_verts: int, num_vertex_loops: int
    ) -> Tuple[Points2D, List[Points2D]]:
        """Get or create reusable vertex buffer for interpolation

        Buffers are cached to avoid creating new Point2D lists for every frame.
        Each buffer is sized for a specific (num_vertices, num_vertex_loops ) combination.

        Args:
            num_verts: Number of vertices in the outer contour
            num_vertex_loops : Number of vertex loops in the shape

        Returns:
            Tuple of (outer_buffer, hole_buffers) where:
            - outer_buffer: List of Point2D for outer contour
            - hole_buffers: List of Lists of Point2D, one per hole
        """
        key = (num_verts, num_vertex_loops)
        if key not in self._vertex_buffer_cache:
            # Create new buffer with pre-allocated Point2D objects
            outer_buffer = [Point2D(0.0, 0.0) for _ in range(num_verts)]
            hole_buffers = [
                [Point2D(0.0, 0.0) for _ in range(num_verts)]
                for _ in range(num_vertex_loops)
            ]
            self._vertex_buffer_cache[key] = (outer_buffer, hole_buffers)

        return self._vertex_buffer_cache[key]

    def _ensure_shapes_matched(
        self,
        field_name: str,
        segment_idx: int,
        states1: List[State],
        states2: List[State]
    ) -> Tuple[List[State], List[State]]:
        """Cache M→N shape matching for list fields

        Similar to vertex buffer caching, but for shape list matching.
        Performs M→N matching once per segment and caches the result.

        Args:
            field_name: Name of the field (e.g., "clip_states")
            segment_idx: Index of the keystate segment
            states1: Source states
            states2: Destination states

        Returns:
            Tuple of (matched_states1, matched_states2)
        """
        cache_key = (field_name, segment_idx)

        if cache_key in self._shape_list_cache:
            return self._shape_list_cache[cache_key]

        # Get mapper from config (reuse hole matching config)
        from vood.transition.align_vertices import (
            _get_vertex_loop_mapper_from_config
        )
        mapper = _get_vertex_loop_mapper_from_config()

        # Convert to loops using interpolation engine helpers
        from vood.transition.interpolation_engine import InterpolationEngine
        # Create a temporary engine instance to access helper methods
        engine = InterpolationEngine(
            easing_resolver=self._easing_resolver
        )

        loops1 = [engine._state_to_vertex_loop(s) for s in states1]
        loops2 = [engine._state_to_vertex_loop(s) for s in states2]

        # Match
        matched_loops1, matched_loops2 = mapper.map(loops1, loops2)

        # Convert back
        matched_states1 = engine._loops_to_states(matched_loops1, states1)
        matched_states2 = engine._loops_to_states(matched_loops2, states2)

        # Cache and return
        result = (matched_states1, matched_states2)
        self._shape_list_cache[cache_key] = result
        return result
