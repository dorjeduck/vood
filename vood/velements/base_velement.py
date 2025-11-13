"""Base element class with shared keyframe animation logic"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Tuple, Callable, Dict, Any
from dataclasses import fields, replace

import drawsvg as dw

from vood.components import State
from vood.components.states.path import MorphMethod
from vood.paths import SVGPath
from vood.utils.colors import hex_to_color
from vood.transitions import interpolation
from vood.transitions.interpolation import NativeMorpher, FlubberMorpher


class BaseVElement(ABC):
    """Abstract base class for all animatable elements

    Provides shared keyframe animation logic for Element and ContainerElement.

    Elements only exist (render) within their keyframe time range. Outside this range,
    render_at_frame_time returns None.
    """

    def __init__(
        self,
        state: Optional[State] = None,
        states: Optional[Iterable[State]] = None,
        keyframes: Optional[Iterable[Tuple[float, State]]] = None,
        global_transitions: Optional[Dict[str, Tuple[Any, Any]]] = None,
        easing: Optional[Dict[str, Callable[[float], float]]] = None,
        segment_easing: Optional[Dict[int, Dict[str, Callable[[float], float]]]] = None,
    ) -> None:
        """Initialize keyframe animation system

        Args:
            state: Single state for static element
            states: List of states for evenly-timed animation
            keyframes: List of (frame_time, state) tuples for precise timing.
                Element will only exist between first and last keyframe times.
            global_transitions: Dict of property_name -> (start_value, end_value)
                for properties that should transition linearly across entire animation
                independent of keyframe structure
            easing: Optional dict to override default easing functions for all segments
            segment_easing: Optional dict of segment_index -> {property: easing_func}
                to override easing for specific segments. Segment 0 is between keyframe[0]
                and keyframe[1], segment 1 is between keyframe[1] and keyframe[2], etc.
        """

        # --- 1. Input Validation: Ensure ONLY ONE source is provided ---
        provided_inputs = [arg for arg in [state, states, keyframes] if arg is not None]
        count = len(provided_inputs)

        if count == 0:
            # Enforce that a state must be provided.
            raise ValueError(
                "VElement requires configuration: provide 'state', 'states', or 'keyframes'."
            )

        if count > 1:
            # CRITICAL CHECK: Block conflicting definitions
            raise ValueError(
                f"Conflicting inputs provided ({count} specified). "
                "Please specify only one of 'state', 'states', or 'keyframes'."
            )

        self.easing_overrides = easing or {}
        self.segment_easing = segment_easing or {}
        self.global_transitions = global_transitions or {}
        self.keyframes: List[Tuple[float, State]] = []
        self._current_global_t: float = 0.0  # Track global animation time
        self._current_segment_index: int = 0  # Track which segment we're in

        if state is not None:
            if isinstance(state, Iterable):
                raise ValueError("state must be a single State instance, not a list")
            self.set_state(state)
        elif states is not None:
            if isinstance(states, Iterable):
                for s in states:
                    if not isinstance(s, State):
                        raise ValueError("states must be a list of State instances")
                self.set_states(states)
            else:
                raise ValueError("states must be a list of State instances")
        elif keyframes is not None:
            self.set_keyframes(keyframes)

            # Normalize global_transitions colors
        if global_transitions:
            self.global_transitions = {}
            for key, (start, end) in global_transitions.items():
                if isinstance(start, str) and start.startswith("#"):
                    start = hex_to_color(start)
                if isinstance(end, str) and end.startswith("#"):
                    end = hex_to_color(end)
                self.global_transitions[key] = (start, end)
        else:
            self.global_transitions = {}

    def set_state(self, state: State) -> None:
        """Set a single static state

        Creates a keyframe at time 0.0, making the element visible for the entire timeline.
        """
        self.keyframes = [(0.0, state)]

    def set_states(self, states: List[State]) -> None:
        """Set evenly-timed states

        Distributes states evenly across the [0.0, 1.0] timeline.
        """
        if len(states) < 1:
            raise ValueError("states must contain at least one state")

        if len(states) == 1:
            self.keyframes = [(0.0, states[0])]
        else:
            self.keyframes = [
                (i / (len(states) - 1), state) for i, state in enumerate(states)
            ]

    def set_keyframes(self, keyframes: List[Tuple[float, State]]) -> None:
        """Set explicit keyframes

        Element will only exist (be rendered) between the first and last keyframe times.

        Args:
            keyframes: List of (time, state) tuples. Times must be in [0.0, 1.0]

        Example:
            >>> # Element appears at 0.3 and disappears after 0.8
            >>> element.set_keyframes([
            ...     (0.3, State(x=0)),
            ...     (0.8, State(x=100))
            ... ])
            >>> # At t=0.0-0.3: returns None (not rendered)
            >>> # At t=0.3-0.8: interpolates normally
            >>> # At t=0.8-1.0: returns None (not rendered)
        """
        if not keyframes:
            raise ValueError("keyframes cannot be empty")
        keyframes.sort(key=lambda x: x[0])
        for t, _ in keyframes:
            if not (0.0 <= t <= 1.0):
                raise ValueError(f"Keyframe times must be between 0.0 and 1.0, got {t}")
        self.keyframes = keyframes

    @abstractmethod
    def render(self) -> Optional[dw.DrawingElement]:
        """Render the element in its initial state (static rendering)

        Returns:
            drawsvg element representing the element, or None if element doesn't exist at t=0
        """
        if not self.keyframes:
            raise ValueError("No state, states, or keyframes set for rendering.")
        # Subclass should implement rendering logic
        pass

    @abstractmethod
    def render_at_frame_time(self, t: float) -> Optional[dw.DrawingElement]:
        """Render the element at a specific animation time

        Args:
            t: Time factor from 0.0 to 1.0

        Returns:
            drawsvg element representing the element at time t, or None if element
            doesn't exist at this time (outside keyframe range)
        """
        if not self.keyframes:
            raise ValueError("No state, states, or keyframes set for rendering.")
        # Subclass should implement rendering logic
        pass

    def is_animatable(self) -> bool:
        """Check if this element can be animated

        Returns:
            True if element has multiple keyframes or has global transitions
        """
        return len(self.keyframes) > 1 or bool(self.global_transitions)

    def _get_state_at_time(self, t: float) -> Optional[State]:
        """Get the interpolated state at a specific time

        Args:
            t: Time factor from 0.0 to 1.0

        Returns:
            Interpolated State at time t, or None if outside keyframe range
        """
        if not self.keyframes:
            return None

        # Get keyframe time range
        first_time = self.keyframes[0][0]
        last_time = self.keyframes[-1][0]

        # Check if time is outside keyframe range
        if t < first_time or t > last_time:
            return None  # Element doesn't exist at this time

        # Store global time for global_transitions
        self._current_global_t = max(0.0, min(1.0, t))

        # Handle exact match with first keyframe or single keyframe
        if t == first_time or len(self.keyframes) == 1:
            base_state = self.keyframes[0][1]
            # Apply global transitions even for static/single keyframe
            if self.global_transitions:
                return self._apply_global_transitions(
                    base_state, self._current_global_t
                )
            return base_state

        # Find the two keyframes to interpolate between
        for i in range(len(self.keyframes) - 1):
            t1, state1 = self.keyframes[i]
            t2, state2 = self.keyframes[i + 1]

            if t1 <= t <= t2:
                # Found the right segment
                self._current_segment_index = i  # Store segment index

                if t1 == t2:  # Instant transition at same time
                    # Return state2 (the "after" state) for instant transitions
                    if self.global_transitions:
                        return self._apply_global_transitions(
                            state2, self._current_global_t
                        )
                    return state2

                # Calculate segment progress
                segment_t = (t - t1) / (t2 - t1)

                # Create interpolated state
                interpolated_state = self._create_eased_state(
                    state1, state2, segment_t, i
                )
                return interpolated_state

        # If we get here, t equals the last keyframe time exactly
        final_state = self.keyframes[-1][1]
        if self.global_transitions:
            return self._apply_global_transitions(final_state, self._current_global_t)
        return final_state

    def _apply_global_transitions(self, base_state: State, global_t: float) -> State:
        """Apply global transitions to a state

        Args:
            base_state: The base state to modify
            global_t: Global animation time (0.0 to 1.0)

        Returns:
            New state with global transitions applied
        """
        if not self.global_transitions:
            return base_state

        # Get the default easing functions from the state class
        default_easing = getattr(base_state, "DEFAULT_EASING", {})

        updates = {}

        for field_name, (start_value, end_value) in self.global_transitions.items():
            # Get the easing function for this property
            easing_func = self.easing_overrides.get(
                field_name, default_easing.get(field_name)
            )

            # Apply easing to global time
            eased_t = easing_func(global_t) if easing_func else global_t

            # Determine interpolation method based on value type
            if isinstance(start_value, SVGPath):
                # SVG Path interpolation
                updates[field_name] = NativeMorpher(
                    start_value, end_value
                )(eased_t)

            elif isinstance(start_value, tuple) and len(start_value) == 3:
                # Color interpolation
                updates[field_name] = interpolation.color(
                    start_value, end_value, eased_t
                )
            elif hasattr(base_state, "is_angle"):
                # Check if this field is an angle
                field_obj = next(
                    (f for f in fields(base_state) if f.name == field_name), None
                )
                if field_obj and base_state.is_angle(field_obj):
                    updates[field_name] = interpolation.angle(
                        start_value, end_value, eased_t
                    )
                else:
                    updates[field_name] = interpolation.lerp(
                        start_value, end_value, eased_t
                    )
            elif isinstance(start_value, (int, float)):
                # Numeric interpolation
                updates[field_name] = interpolation.lerp(
                    start_value, end_value, eased_t
                )
            else:

                # For non-numeric values, switch at t=0.5
                updates[field_name] = start_value if eased_t < 0.5 else end_value

        return replace(base_state, **updates)

    def _create_eased_state(
        self, start_state: State, end_state: State, t: float, segment_index: int
    ) -> State:
        """Create an interpolated state using per-property easing functions

        Args:
            start_state: Starting state
            end_state: Ending state
            t: Time factor from 0.0 to 1.0 (segment time, not global time)
            segment_index: Index of the current segment (0-based)

        Returns:
            New state with interpolated values using appropriate easing per property
        """
        # Get the default easing functions from the state class
        default_easing = getattr(start_state, "DEFAULT_EASING", {})

        # Get segment-specific easing overrides if available
        segment_overrides = self.segment_easing.get(segment_index, {})

        # Start with the start state values
        interpolated_values = {}

        # Interpolate each field
        for field in fields(start_state):
            field_name = field.name

            # Skip properties that have global transitions - they'll be applied later
            if field_name in self.global_transitions:
                continue

            start_value = getattr(start_state, field_name)
            end_value = getattr(end_state, field_name)

            # Skip if values are the same (no animation needed)
            if start_value == end_value:
                interpolated_values[field_name] = start_value
                continue

            # Get the easing function for this property with priority:
            # 1. Segment-specific override
            # 2. Global property override
            # 3. Default easing from state
            easing_func = (
                segment_overrides.get(field_name)
                or self.easing_overrides.get(field_name)
                or default_easing.get(field_name)
            )

            # Apply easing to time parameter
            if easing_func:
                eased_t = easing_func(t)
            else:
                eased_t = t  # Default to linear if no easing function specified

            # Interpolate the value using the eased time

            if isinstance(start_value, SVGPath):

                morph_method = getattr(start_state, "morph_method", None)

                # Choose interpolation method
                if morph_method == MorphMethod.SHAPE or morph_method == "shape":
                    interpolated_values[field_name] = (
                        FlubberMorpher.for_paths(start_value, end_value)(
                            eased_t
                        )
                    )
                elif morph_method == MorphMethod.STROKE or morph_method == "stroke":
                    interpolated_values[field_name] = (
                        NativeMorpher.for_paths(start_value, end_value)(
                            eased_t
                        )
                    )
                else:  # None or AUTO
                    # Auto-detect based on path
                    if self._path_is_closed(start_value):
                        interpolated_values[field_name] = (
                            FlubberMorpher.for_paths(
                                start_value, end_value
                            )(eased_t)
                        )
                    else:
                        interpolated_values[field_name] = (
                            NativeMorpher.for_paths(
                                start_value, end_value
                            )(eased_t)
                        )

            elif isinstance(start_value, tuple) and len(start_value) == 3:
                # Color interpolation
                interpolated_values[field_name] = interpolation.color(
                    start_value, end_value, eased_t
                )
            elif start_state.is_angle(field):
                # Angle interpolation
                interpolated_values[field_name] = interpolation.angle(
                    start_value, end_value, eased_t
                )
            elif isinstance(start_value, (int, float)):
                # Numeric interpolation
                interpolated_values[field_name] = interpolation.lerp(
                    start_value, end_value, eased_t
                )
            else:

                # For non-numeric values, just switch at t=0.5 (stepped animation)
                interpolated_values[field_name] = interpolation.step(
                    start_value, end_value, eased_t
                )

        # Create new state with interpolated values
        interpolated_state = replace(start_state, **interpolated_values)

        # Apply global transitions on top of keyframe interpolation
        if self.global_transitions:
            interpolated_state = self._apply_global_transitions(
                interpolated_state, self._current_global_t
            )

        return interpolated_state

    def _path_is_closed(self, path: SVGPath, tolerance: float = 0.01) -> bool:
        """Check if path is closed (ends with Z or returns to start point)"""

        # Check if path string ends with Z (covers ClosePath command)
        # print with type path is

        path_str = path.to_string().strip().upper()

        if path_str.endswith("Z"):
            return True

        # Check if start and end points are the same
        if len(path.commands) < 2:
            return False

        # Get start and end points
        start_cmd = path.commands[0]
        end_cmd = path.commands[-1]

        if not (hasattr(start_cmd, "x") and hasattr(end_cmd, "x")):
            return False

        # Check distance
        distance = (
            (end_cmd.x - start_cmd.x) ** 2 + (end_cmd.y - start_cmd.y) ** 2
        ) ** 0.5
        return distance <= tolerance
