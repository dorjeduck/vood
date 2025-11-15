"""State and value interpolation engine"""

from typing import Any, Callable, Dict, Optional
from dataclasses import fields, replace

from vood.components import State
from vood.components.states.path import MorphMethod
from vood.paths import SVGPath
from vood.transitions import interpolation
from vood.transitions.interpolation import NativeMorpher, FlubberMorpher
from vood.core.color import Color


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
    ) -> State:
        """
        Create an interpolated state between two keystates.

        Args:
            start_state: Starting state
            end_state: Ending state
            t: Interpolation parameter (0.0 to 1.0)
            segment_easing_overrides: Optional segment-level easing overrides
            property_keystates_fields: Set of field names managed by property_keystates

        Returns:
            Interpolated state
        """
        interpolated_values = {}

        for field in fields(start_state):
            field_name = field.name

            # Skip fields managed by property_keystates (they're handled separately)
            if field_name in property_keystates_fields:
                continue

            start_value = getattr(start_state, field_name)
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
                start_state, field_name, start_value, end_value, eased_t
            )

        return replace(start_state, **interpolated_values)

    def interpolate_value(
        self,
        state: State,
        field_name: str,
        start_value: Any,
        end_value: Any,
        eased_t: float,
    ) -> Any:
        """
        Interpolate a single value based on its type and context.

        Args:
            state: State object for context (e.g., morph method for paths)
            field_name: Name of the field being interpolated
            start_value: Starting value
            end_value: Ending value
            eased_t: Eased interpolation parameter (0.0 to 1.0)

        Returns:
            Interpolated value
        """

        if (
            field_name == "vertices"
            and isinstance(start_value, list)
            and isinstance(end_value, list)
        ):
            if len(start_value) != len(end_value):
                raise ValueError(
                    f"Vertex lists must have same length: {len(start_value)} != {len(end_value)}"
                )
            return [
                (
                    interpolation.lerp(v1[0], v2[0], eased_t),
                    interpolation.lerp(v1[1], v2[1], eased_t),
                )
                for v1, v2 in zip(start_value, end_value)
            ]

        # 1. SVG Path interpolation
        if isinstance(start_value, SVGPath):
            return self._interpolate_path(state, start_value, end_value, eased_t)

        # 2. Color interpolation
        if isinstance(start_value, Color):
            return start_value.interpolate(end_value, eased_t)

        # 3. Angle interpolation (handles wraparound)
        if self._is_angle_field(state, field_name):
            return interpolation.angle(start_value, end_value, eased_t)

        # 4. Numeric interpolation
        if isinstance(start_value, (int, float)):
            return interpolation.lerp(start_value, end_value, eased_t)

        # 5. Non-numeric values: step function at t=0.5
        return interpolation.step(start_value, end_value, eased_t)

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
