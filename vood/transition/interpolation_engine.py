"""State and value interpolation engine"""

from typing import Any, Callable, Dict, Optional, Tuple, List
from dataclasses import fields, replace
import logging

from vood.component import State
from vood.component.state.path import MorphMethod
from vood.component.vertex.vertex_contours import VertexContours
from vood.component.vertex.vertex_loop import VertexLoop
from vood.path import SVGPath
from vood.transition import lerp, step, angle, inbetween, circular_midpoint
from vood.transition.morpher import NativeMorpher, FlubberMorpher
from vood.core.color import Color

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
                interpolated_values[field_name] = start_value if t < 0.5 else getattr(end_state, field_name, start_value)
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
                start_state, end_state, field_name, start_value, end_value, eased_t, vertex_buffer
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

            # Interpolate outer vertices
            if vertex_buffer:
                # Optimized path: Use pre-allocated buffer with in-place operations
                outer_buffer, hole_buffers = vertex_buffer
                num_verts = len(start_value.outer.vertices)

                # Resize buffer if needed (grow only, never shrink)
                if len(outer_buffer) < num_verts:
                    from vood.core.point2d import Point2D
                    outer_buffer.extend(Point2D(0.0, 0.0) for _ in range(num_verts - len(outer_buffer)))

                # In-place interpolation using ilerp
                for i, (v1, v2) in enumerate(zip(start_value.outer.vertices, end_value.outer.vertices)):
                    p = outer_buffer[i]
                    p.x = v1.x
                    p.y = v1.y
                    p.ilerp(v2, eased_t)  # Mutate in place

                # Use slice of buffer (not the whole buffer, only the vertices we need)
                interpolated_vertices = outer_buffer[:num_verts]
            else:
                # Fallback: Original behavior (for backward compatibility)
                interpolated_vertices = [
                    (
                        lerp(v1.x, v2.x, eased_t),
                        lerp(v1.y, v2.y, eased_t),
                    )
                    for v1, v2 in zip(start_value.outer.vertices, end_value.outer.vertices)
                ]

            # Force closure ONLY if BOTH states are closed
            start_closed = getattr(
                start_state, "closed", True
            )  # Default True for closed shapes
            end_closed = getattr(end_state, "closed", True)

            if start_closed and end_closed and len(interpolated_vertices) > 1:
                interpolated_vertices[-1] = interpolated_vertices[0]

            # Interpolate holes
            interpolated_holes = []
            start_holes = start_value.holes
            end_holes = end_value.holes

            # Holes should have been matched during alignment, so counts should match
            if len(start_holes) != len(end_holes):
                # Fallback: if counts don't match, just use start or end based on t
                logger.warning(
                    f"Hole count mismatch during interpolation: {len(start_holes)} != {len(end_holes)}. "
                    f"This should not happen if vertex alignment was performed correctly. "
                    f"Using step interpolation at t=0.5 as fallback."
                )
                interpolated_holes = start_holes if eased_t < 0.5 else end_holes
            else:
                # Interpolate each matched hole pair
                for hole_idx, (hole1, hole2) in enumerate(zip(start_holes, end_holes)):
                    if len(hole1.vertices) != len(hole2.vertices):
                        # If vertex counts don't match, just switch at t=0.5
                        logger.warning(
                            f"Hole {hole_idx} vertex count mismatch: {len(hole1.vertices)} != {len(hole2.vertices)}. "
                            f"This should not happen if hole alignment was performed correctly. "
                            f"Using step interpolation at t=0.5 as fallback."
                        )
                        interpolated_holes.append(hole1 if eased_t < 0.5 else hole2)
                    else:
                        # Interpolate hole vertices
                        if vertex_buffer and hole_idx < len(hole_buffers):
                            # Optimized path: Use pre-allocated hole buffer
                            hole_buffer = hole_buffers[hole_idx]
                            num_hole_verts = len(hole1.vertices)

                            # Resize hole buffer if needed
                            if len(hole_buffer) < num_hole_verts:
                                from vood.core.point2d import Point2D
                                hole_buffer.extend(Point2D(0.0, 0.0) for _ in range(num_hole_verts - len(hole_buffer)))

                            # In-place interpolation for hole vertices
                            for i, (v1, v2) in enumerate(zip(hole1.vertices, hole2.vertices)):
                                p = hole_buffer[i]
                                p.x = v1.x
                                p.y = v1.y
                                p.ilerp(v2, eased_t)

                            interp_hole_verts = hole_buffer[:num_hole_verts]
                        else:
                            # Fallback: Original behavior
                            interp_hole_verts = [
                                (
                                    lerp(v1.x, v2.x, eased_t),
                                    lerp(v1.y, v2.y, eased_t),
                                )
                                for v1, v2 in zip(hole1.vertices, hole2.vertices)
                            ]

                        # Ensure hole closure
                        if len(interp_hole_verts) > 1:
                            interp_hole_verts[-1] = interp_hole_verts[0]

                        interpolated_holes.append(VertexLoop(interp_hole_verts, closed=True))

            # Return a VertexContours object with interpolated outer and holes
            return VertexContours(
                outer=VertexLoop(interpolated_vertices, closed=start_closed and end_closed),
                holes=interpolated_holes if interpolated_holes else None
            )

        # 1. SVG Path interpolation
        if isinstance(start_value, SVGPath):
            return self._interpolate_path(start_state, start_value, end_value, eased_t)

        # 2. Color interpolation
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
