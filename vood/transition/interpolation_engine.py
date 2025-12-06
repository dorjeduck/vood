"""State and value interpolation engine"""

from typing import Any, Callable, Dict, Optional, Tuple, List
from dataclasses import fields, replace
import logging

from vood.component import State
from vood.component.effect.gradient.base import Gradient
from vood.component.effect.pattern.base import Pattern
from vood.component.effect.filter.base import Filter
from vood.component.state.path import MorphMethod
from vood.component.vertex.vertex_contours import VertexContours
from vood.component.vertex.vertex_loop import VertexLoop
from vood.path import SVGPath
from vood.transition import lerp, step, angle, inbetween, circular_midpoint
from vood.transition.morpher import NativeMorpher, FlubberMorpher
from vood.core.color import Color
from vood.transition.shape_list_interpolator import (
    ShapeListInterpolator,
    _normalize_to_state_list,
)

logger = logging.getLogger(__name__)


class InterpolationEngine:
    """Handles interpolation of states and individual values"""

    def __init__(self, easing_resolver):
        """
        Initialize the interpolation engine.

        Args:
            easing_resolver: EasingResolver instance for determining easing functions
        """
        self.easing_resolver = easing_resolver
        self._shape_list_interpolator = ShapeListInterpolator(self)

    def create_eased_state(
        self,
        start_state: State,
        end_state: State,
        t: float,
        segment_easing_overrides: Optional[Dict[str, Callable[[float], float]]],
        property_keystates_fields: set,
        vertex_buffer: Optional[Tuple[List, List[List]]] = None,
    ) -> State:
        """
        Create an interpolated state between two keystates.

        Args:
            start_state: Starting state
            end_state: Ending state
            t: Interpolation parameter (0.0 to 1.0)
            segment_easing_overrides: Per-segment easing overrides
            property_keystates_fields: Fields managed by property keystates
            vertex_buffer: Optional reusable buffer for vertex interpolation
        """
        interpolated_values = {}

        # if t == 0:
        #    return start_state
        # elif t == 1:
        #    return end_state

        for field in fields(start_state):
            field_name = field.name

            # Skip fields managed by property_keystates
            if field_name in property_keystates_fields:
                continue

            # Skip non-interpolatable fields (structural/configuration properties)
            if field_name in start_state.NON_INTERPOLATABLE_FIELDS:
                start_value = getattr(start_state, field_name)
                interpolated_values[field_name] = (
                    start_value
                    if t < 0.5
                    else getattr(end_state, field_name, start_value)
                )
                continue

            start_value = getattr(start_state, field_name)

            if not hasattr(end_state, field_name):
                continue

            end_value = getattr(end_state, field_name)

            # No interpolation needed if values are identical
            if start_value == end_value:
                interpolated_values[field_name] = start_value
                continue

            # Get easing function for this field
            easing_func = self.easing_resolver.get_easing_for_field(
                start_state, field_name, segment_easing_overrides
            )
            eased_t = easing_func(t) if easing_func else t

            # Interpolate the value
            interpolated_values[field_name] = self.interpolate_value(
                start_state,
                end_state,
                field_name,
                start_value,
                end_value,
                eased_t,
                vertex_buffer,
            )

        # return replace(start_state, **interpolated_values)

        if t < 0.5:
            return replace(start_state, **interpolated_values)
        else:
            return replace(end_state, **interpolated_values)

    def interpolate_value(
        self,
        start_state: State,
        end_state: State,
        field_name: str,
        start_value: Any,
        end_value: Any,
        eased_t: float,
        vertex_buffer: Optional[Tuple[List, List[List]]] = None,
    ) -> Any:
        """
        Interpolate a single value based on its type and context.

        Args:
            state: State object for context (e.g., morph method for paths)
            field_name: Name of the field being interpolated
            start_value: Starting value
            end_value: Ending value
            eased_t: Eased interpolation parameter (0.0 to 1.0)
            vertex_buffer: Optional reusable buffer for vertex interpolation
                          (outer_buffer, hole_buffers) to avoid allocations

        Returns:
            Interpolated value
        """
        # Check for List[State] interpolation (clip_states, mask_states, etc.)
        # IMPORTANT: Only normalize if we have actual lists, not single State objects
        # This prevents infinite recursion when interpolating states within lists
        is_list_field = isinstance(start_value, list) or isinstance(end_value, list)

        if is_list_field:
            start_list = _normalize_to_state_list(start_value)
            end_list = _normalize_to_state_list(end_value)

            if start_list is not None and end_list is not None:
                # Both are state lists (or normalizable to lists)
                return self._shape_list_interpolator.interpolate_state_list(
                    start_list, end_list, eased_t
                )

        if (
            field_name == "_aligned_contours"
            and isinstance(start_value, VertexContours)
            and isinstance(end_value, VertexContours)
        ):

            # Handle empty contours - use step interpolation at midpoint
            if not start_value or not end_value:
                logger.warning(
                    "One or both contours are empty during interpolation. "
                    "Using step interpolation at t=0.5. This may indicate a "
                    "problem with contour generation."
                )
                return start_value if eased_t < 0.5 else end_value

            if len(start_value.outer) != len(end_value.outer):
                raise ValueError(
                    f"Vertex lists must have same length: {len(start_value.outer)} != {len(end_value.outer)}. "
                    f"Ensure both states have the same num_vertices parameter."
                )

            # Force closure ONLY if BOTH states are closed
            start_closed = getattr(
                start_state, "closed", True
            )  # Default True for closed shapes
            end_closed = getattr(end_state, "closed", True)

            # Interpolate outer vertices
            outer_buffer = vertex_buffer[0] if vertex_buffer else None
            interpolated_vertices = self._interpolate_vertex_list(
                start_value.outer.vertices,
                end_value.outer.vertices,
                eased_t,
                buffer=outer_buffer,
                ensure_closure=(start_closed and end_closed),
            )

            # Interpolate  vertex_loops
            interpolated_vertex_loops = []
            start_vertex_loops = start_value.holes
            end_vertex_loops = end_value.holes

            # vertex loops should have been matched during alignment, so counts should match
            if len(start_vertex_loops) != len(end_vertex_loops):
                # Fallback: if counts don't match, just use start or end based on t
                logger.warning(
                    f"Hole count mismatch during interpolation: {len(start_vertex_loops )} != {len(end_vertex_loops )}. "
                    f"This should not happen if vertex alignment was performed correctly. "
                    f"Using step interpolation at t=0.5 as fallback."
                )
                interpolated_vertex_loops = (
                    start_vertex_loops if eased_t < 0.5 else end_vertex_loops
                )
            else:
                # Interpolate each matched hole pair
                for hole_idx, (hole1, hole2) in enumerate(
                    zip(start_vertex_loops, end_vertex_loops)
                ):
                    if len(hole1.vertices) != len(hole2.vertices):
                        # If vertex counts don't match, just switch at t=0.5
                        logger.warning(
                            f"Hole {hole_idx} vertex count mismatch: {len(hole1.vertices)} != {len(hole2.vertices)}. "
                            f"This should not happen if hole alignment was performed correctly. "
                            f"Using step interpolation at t=0.5 as fallback."
                        )
                        interpolated_vertex_loops.append(
                            hole1 if eased_t < 0.5 else hole2
                        )
                    else:
                        # Interpolate hole vertices
                        hole_buffers = vertex_buffer[1] if vertex_buffer else []
                        hole_buffer = (
                            hole_buffers[hole_idx]
                            if (vertex_buffer and hole_idx < len(hole_buffers))
                            else None
                        )
                        interp_hole_verts = self._interpolate_vertex_list(
                            hole1.vertices,
                            hole2.vertices,
                            eased_t,
                            buffer=hole_buffer,
                            ensure_closure=True,  # Holes always closed
                        )

                        interpolated_vertex_loops.append(
                            VertexLoop(interp_hole_verts, closed=True)
                        )

            # Return a VertexContours object with interpolated outer and  vertex_loops
            return VertexContours(
                outer=VertexLoop(
                    interpolated_vertices, closed=start_closed and end_closed
                ),
                holes=(
                    interpolated_vertex_loops if interpolated_vertex_loops else None
                ),
            )

        # 1. State interpolation (for clip_state, mask_state)
        if isinstance(start_value, State) and isinstance(end_value, State):
            # Check if this is a morph between different VertexState types
            from vood.component.state.base_vertex import VertexState

            if (
                isinstance(start_value, VertexState)
                and isinstance(end_value, VertexState)
                and type(start_value) != type(end_value)
            ):
                # Need to align vertices for morphing
                from vood.transition.align_vertices import get_aligned_vertices

                contours1_aligned, contours2_aligned = get_aligned_vertices(
                    start_value, end_value
                )
                start_value = replace(start_value, _aligned_contours=contours1_aligned)
                end_value = replace(end_value, _aligned_contours=contours2_aligned)

            # Recursively interpolate the clip/mask state
            return self.create_eased_state(
                start_value,
                end_value,
                eased_t,
                segment_easing_overrides=None,
                property_keystates_fields=set(),
                vertex_buffer=None,  # Don't use vertex buffer for clips
            )

        # Handle State ↔ None transitions
        if (
            isinstance(start_value, Gradient)
            or isinstance(start_value, Pattern)
            or isinstance(start_value, Filter)
        ):
            return start_value.interpolate(end_value, eased_t)

        if isinstance(start_value, State) and end_value is None:
            # Fade out: opacity → 0
            return replace(start_value, opacity=lerp(start_value.opacity, 0.0, eased_t))
        if start_value is None and isinstance(end_value, State):
            # Fade in: opacity from 0
            return replace(end_value, opacity=lerp(0.0, end_value.opacity, eased_t))

        # 2. SVG Path interpolation
        if isinstance(start_value, SVGPath):
            return self._interpolate_path(start_state, start_value, end_value, eased_t)

        # 3. Color interpolation
        if isinstance(start_value, Color):
            return start_value.interpolate(end_value, eased_t)

        # 3. Angle interpolation (handles wraparound)
        if self._is_angle_field(start_state, field_name):
            return angle(start_value, end_value, eased_t)

        # 4. Numeric interpolation
        if isinstance(start_value, (int, float)):
            return lerp(start_value, end_value, eased_t)

        # 5. Non-numeric values: step function at t=0.5
        return step(start_value, end_value, eased_t)

    def _interpolate_path(
        self,
        state: State,
        start_path: SVGPath,
        end_path: SVGPath,
        eased_t: float,
    ) -> SVGPath:
        """
        Interpolate between two SVG paths using appropriate morphing method.

        Morph method priority:
        1. Explicit morph_method on state
        2. Auto-detect: closed paths use shape morph, open paths use stroke morph

        Args:
            state: State containing optional morph_method
            start_path: Starting SVG path
            end_path: Ending SVG path
            eased_t: Eased interpolation parameter

        Returns:
            Interpolated SVG path
        """
        morph_method = getattr(state, "morph_method", None)

        # Explicit shape morph
        if morph_method == MorphMethod.SHAPE or morph_method == "shape":
            return FlubberMorpher.for_paths(start_path, end_path)(eased_t)

        # Explicit stroke morph
        if morph_method == MorphMethod.STROKE or morph_method == "stroke":
            return NativeMorpher.for_paths(start_path, end_path)(eased_t)

        # Auto-detect: use shape morph for closed paths, stroke for open
        if self._path_is_closed(start_path):
            return FlubberMorpher.for_paths(start_path, end_path)(eased_t)
        else:
            return NativeMorpher.for_paths(start_path, end_path)(eased_t)

    def _is_angle_field(self, state: State, field_name: str) -> bool:
        """
        Check if a field represents an angle value.

        Args:
            state: State object
            field_name: Name of the field to check

        Returns:
            True if field represents an angle
        """
        if not hasattr(state, "is_angle"):
            return False

        field_obj = next((f for f in fields(state) if f.name == field_name), None)
        if field_obj:
            return state.is_angle(field_obj)

        return False

    def _path_is_closed(self, path: SVGPath, tolerance: float = 0.01) -> bool:
        """
        Check if an SVG path is closed.

        A path is considered closed if:
        1. It ends with a 'Z' command, or
        2. The start and end points are within tolerance distance

        Args:
            path: SVG path to check
            tolerance: Maximum distance between start/end points to consider closed

        Returns:
            True if path is closed
        """
        # Check for explicit 'Z' close command
        path_str = path.to_string().strip().upper()
        if path_str.endswith("Z"):
            return True

        # Check if start and end points are close enough
        if len(path.commands) < 2:
            return False

        start_cmd = path.commands[0]
        end_cmd = path.commands[-1]

        if not (hasattr(start_cmd, "x") and hasattr(end_cmd, "x")):
            return False

        distance = (
            (end_cmd.x - start_cmd.x) ** 2 + (end_cmd.y - start_cmd.y) ** 2
        ) ** 0.5

        return distance <= tolerance

    def _interpolate_vertex_list(
        self,
        vertices1: List,
        vertices2: List,
        eased_t: float,
        buffer: Optional[List] = None,
        ensure_closure: bool = False,
    ) -> List:
        """Interpolate between two vertex lists with optional buffer optimization

        Args:
            vertices1: Start vertices
            vertices2: End vertices (must match length)
            eased_t: Interpolation parameter
            buffer: Optional pre-allocated buffer for in-place operations
            ensure_closure: If True, force last vertex to equal first

        Returns:
            List of interpolated vertices (tuples or Point2D objects)
        """
        if len(vertices1) != len(vertices2):
            raise ValueError(
                f"Vertex lists must have same length: {len(vertices1)} != {len(vertices2)}"
            )

        if buffer:
            # Optimized path: Use pre-allocated buffer with in-place operations
            num_verts = len(vertices1)

            # Resize buffer if needed (grow only, never shrink)
            if len(buffer) < num_verts:
                from vood.core.point2d import Point2D

                buffer.extend(Point2D(0.0, 0.0) for _ in range(num_verts - len(buffer)))

            # In-place interpolation using ilerp
            for i, (v1, v2) in enumerate(zip(vertices1, vertices2)):
                p = buffer[i]
                p.x = v1.x
                p.y = v1.y
                p.ilerp(v2, eased_t)  # Mutate in place

            interpolated_vertices = buffer[:num_verts]
        else:
            # Fallback: Original behavior (for backward compatibility)
            interpolated_vertices = [
                (lerp(v1.x, v2.x, eased_t), lerp(v1.y, v2.y, eased_t))
                for v1, v2 in zip(vertices1, vertices2)
            ]

        # Ensure closure if requested
        if ensure_closure and len(interpolated_vertices) > 1:
            interpolated_vertices[-1] = interpolated_vertices[0]

        return interpolated_vertices
