"""Shape list interpolation for M→N morphing

Handles interpolation between lists of states using vertex_loop_mapping strategies.
Used for clip_states, mask_states, and general List[State] fields.
"""

from typing import Any, List, Optional
from dataclasses import replace
import logging

from vood.component import State
from vood.component.state.base_vertex import VertexState
from vood.component.vertex.vertex_loop import VertexLoop
from vood.core.point2d import Point2D

logger = logging.getLogger(__name__)


def _normalize_to_state_list(value: Any) -> Optional[List[State]]:
    """Normalize convenience fields to List[State]

    - None → []
    - State → [State]
    - List[State] → List[State]
    - Other → None (not a state field)
    """
    if value is None:
        return []
    elif isinstance(value, State):
        return [value]
    elif isinstance(value, list) and all(isinstance(s, State) for s in value):
        return value
    else:
        return None


class ShapeListInterpolator:
    """Handles interpolation between lists of states (M→N morphing)"""

    def __init__(self, interpolation_engine):
        """
        Args:
            interpolation_engine: InterpolationEngine instance for recursive calls
        """
        self.engine = interpolation_engine

    def interpolate_state_list(
        self,
        start_states: List[State],
        end_states: List[State],
        eased_t: float,
        vertex_loop_mapper=None,
    ) -> List[State]:
        """Interpolate between lists of states using M→N matching

        Applies the same vertex_loop_mapping strategies used for holes,
        but operates on outer shapes instead.

        Args:
            start_states: List of states at t=0
            end_states: List of states at t=1
            eased_t: Interpolation parameter
            vertex_loop_mapper: Matching strategy (default from config)

        Returns:
            List of interpolated states at eased_t
        """
        # Handle empty lists
        if len(start_states) == 0 and len(end_states) == 0:
            return []

        # Get mapper from config (reuse hole matching config)
        if vertex_loop_mapper is None:
            from vood.transition.align_vertices import (
                _get_vertex_loop_mapper_from_config
            )
            vertex_loop_mapper = _get_vertex_loop_mapper_from_config()

        # Convert states to VertexLoop for matching
        start_loops = [self._state_to_vertex_loop(s) for s in start_states]
        end_loops = [self._state_to_vertex_loop(s) for s in end_states]

        # Apply M→N matching
        matched_loops1, matched_loops2 = vertex_loop_mapper.map(
            start_loops, end_loops
        )

        # Convert back to matched states
        matched_states1 = self._loops_to_states(matched_loops1, start_states)
        matched_states2 = self._loops_to_states(matched_loops2, end_states)

        # Pre-process for N>M case: Adjust opacity for overlapping shapes
        # When multiple sources converge to same destination, divide both start and
        # destination opacity by number of sources to prevent visual accumulation
        if len(start_states) > len(end_states) and eased_t < 1.0:
            matched_states1, matched_states2 = self._adjust_opacity_for_overlap(
                matched_states1, matched_states2
            )

        # Post-process for N>M case: Handle duplicate destinations
        # All N sources morph independently. At t=1.0, deduplicate to M destinations.
        if len(start_states) > len(end_states) and eased_t >= 1.0:
            matched_states1, matched_states2 = self._deduplicate_destinations(
                matched_states1, matched_states2
            )

        # Interpolate each matched pair
        # Important: Clear nested clip_states/mask_states to prevent infinite recursion
        interpolated_states = []
        for s1, s2 in zip(matched_states1, matched_states2):
            # Strip nested clip/mask states to prevent recursion
            s1_clean = replace(s1, clip_state=None, mask_state=None,
                             clip_states=None, mask_states=None)
            s2_clean = replace(s2, clip_state=None, mask_state=None,
                             clip_states=None, mask_states=None)

            # Recursively interpolate (handles different shape types)
            interpolated = self.engine.interpolate_value(
                start_state=s1_clean,
                end_state=s2_clean,
                field_name="clip_state",  # Use single-state logic
                start_value=s1_clean,
                end_value=s2_clean,
                eased_t=eased_t,
                vertex_buffer=None,  # Don't use buffer for clips
            )

            # At t=1.0, use primitive renderer (remove _aligned_contours)
            if eased_t >= 1.0 and hasattr(interpolated, '_aligned_contours'):
                interpolated = replace(interpolated, _aligned_contours=None)

            interpolated_states.append(interpolated)

        return interpolated_states

    def _adjust_opacity_for_overlap(
        self,
        matched_states1: List[State],
        matched_states2: List[State]
    ) -> tuple[List[State], List[State]]:
        """Adjust opacity when multiple sources converge to same destination"""
        from collections import defaultdict

        # Group by destination position
        dest_groups = defaultdict(list)
        for i, s2 in enumerate(matched_states2):
            dest_key = (round(s2.x, 1), round(s2.y, 1))
            dest_groups[dest_key].append(i)

        # Adjust opacity for groups with multiple sources
        for dest_key, indices in dest_groups.items():
            if len(indices) > 1:
                # Multiple sources → same destination
                # Divide both start and dest opacity by N
                opacity_factor = 1.0 / len(indices)
                for i in indices:
                    # Build replacement dict for opacity properties
                    updates1 = {"opacity": matched_states1[i].opacity * opacity_factor}
                    updates2 = {"opacity": matched_states2[i].opacity * opacity_factor}

                    # Also adjust fill_opacity if present
                    if hasattr(matched_states1[i], "fill_opacity"):
                        updates1["fill_opacity"] = matched_states1[i].fill_opacity * opacity_factor
                    if hasattr(matched_states2[i], "fill_opacity"):
                        updates2["fill_opacity"] = matched_states2[i].fill_opacity * opacity_factor

                    # Also adjust stroke_opacity if present
                    if hasattr(matched_states1[i], "stroke_opacity"):
                        updates1["stroke_opacity"] = matched_states1[i].stroke_opacity * opacity_factor
                    if hasattr(matched_states2[i], "stroke_opacity"):
                        updates2["stroke_opacity"] = matched_states2[i].stroke_opacity * opacity_factor

                    matched_states1[i] = replace(matched_states1[i], **updates1)
                    matched_states2[i] = replace(matched_states2[i], **updates2)

        return matched_states1, matched_states2

    def _deduplicate_destinations(
        self,
        matched_states1: List[State],
        matched_states2: List[State]
    ) -> tuple[List[State], List[State]]:
        """At t=1.0, remove duplicate destinations"""
        from collections import defaultdict

        dest_groups = defaultdict(list)
        for i, s2 in enumerate(matched_states2):
            # Group by destination position
            dest_key = (round(s2.x, 1), round(s2.y, 1))
            dest_groups[dest_key].append(i)

        # Keep only one state per unique destination
        unique_indices = [group[0] for group in dest_groups.values()]
        return (
            [matched_states1[i] for i in unique_indices],
            [matched_states2[i] for i in unique_indices]
        )

    def _state_to_vertex_loop(self, state: State) -> VertexLoop:
        """Convert state to VertexLoop for spatial matching

        Uses the outer contour for VertexState, or position for non-vertex states.
        IMPORTANT: Translates vertices by state's (x, y) position for correct matching.
        """
        if isinstance(state, VertexState):
            contours = state._generate_contours()
            # Translate vertices by state's position for correct spatial matching
            translated_vertices = [
                Point2D(v.x + state.x, v.y + state.y)
                for v in contours.outer.vertices
            ]
            return VertexLoop(translated_vertices, closed=contours.outer.closed)
        else:
            # Non-vertex state: use position for matching
            pos = Point2D(state.x, state.y)
            return VertexLoop([pos, pos, pos, pos], closed=True)

    def _loops_to_states(
        self,
        matched_loops: List[VertexLoop],
        original_states: List[State]
    ) -> List[State]:
        """Map matched loops back to states (handles zero-loops)

        Args:
            matched_loops: Loops from vertex_loop_mapper
            original_states: Original state list (may be empty for creation)

        Returns:
            List of states corresponding to matched loops
        """
        if len(original_states) == 0:
            # Creation case: build zero-states
            return [self._create_zero_state(loop) for loop in matched_loops]

        result = []
        for matched_loop in matched_loops:
            # Find best matching original state by centroid distance
            matched_centroid = matched_loop.centroid()
            best_state = min(
                original_states,
                key=lambda s: matched_centroid.distance_to(
                    self._state_to_vertex_loop(s).centroid()
                )
            )

            # Check if zero-loop (destruction case)
            if self._is_zero_loop(matched_loop):
                result.append(replace(best_state, opacity=0.0))
            else:
                result.append(best_state)

        return result

    def _create_zero_state(self, loop: VertexLoop) -> State:
        """Create zero-opacity state at loop centroid

        Used for shape creation transitions (0→N).
        Returns a PointState at the centroid location with zero opacity.
        """
        from vood.component.state.point import PointState
        centroid = loop.centroid()
        return PointState(
            x=centroid.x,
            y=centroid.y,
            opacity=0.0
        )

    def _is_zero_loop(self, loop: VertexLoop) -> bool:
        """Check if loop is degenerate (all vertices at same point)

        Used to detect destruction case in matched loops.
        """
        if len(loop.vertices) == 0:
            return True
        first = loop.vertices[0]
        return all(
            abs(v.x - first.x) < 0.01 and abs(v.y - first.y) < 0.01
            for v in loop.vertices
        )
