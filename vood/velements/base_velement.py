"""Base element class with shared keyframe animation logic"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Callable, Dict
from dataclasses import fields, replace

import drawsvg as dw

from vood.components import State
from vood.transitions import Interpolation


class BaseVElement(ABC):
    """Abstract base class for all animatable elements

    Provides shared keyframe animation logic for Element and ContainerElement.
    """

    def __init__(
        self,
        state: Optional[State] = None,
        states: Optional[List[State]] = None,
        keyframes: Optional[List[Tuple[float, State]]] = None,
        easing: Optional[Dict[str, Callable[[float], float]]] = None,
    ) -> None:
        """Initialize keyframe animation system

        Args:
            state: Single state for static element
            states: List of states for evenly-timed animation
            keyframes: List of (frame_time, state) tuples for precise timing
            easing: Optional dict to override default easing functions
        """
        self.easing_overrides = easing or {}
        self.keyframes: List[Tuple[float, State]] = []
        if state is not None:
            self.set_state(state)
        elif states is not None:
            self.set_states(states)
        elif keyframes is not None:
            self.set_keyframes(keyframes)

    def set_state(self, state: State) -> None:
        """Set a single static state"""
        self.keyframes = [(0.0, state)]

    def set_states(self, states: List[State]) -> None:
        """Set evenly-timed states"""
        if len(states) < 1:
            raise ValueError("states must contain at least one state")
        self.keyframes = []
        if len(states) == 1:
            self.keyframes = [(0.0, states[0])]
        else:
            for i, state in enumerate(states):
                t = i / (len(states) - 1)
                self.keyframes.append((t, state))

    def set_keyframes(self, keyframes: List[Tuple[float, State]]) -> None:
        """Set explicit keyframes"""
        if not keyframes:
            raise ValueError("keyframes cannot be empty")
        keyframes.sort(key=lambda x: x[0])
        for t, _ in keyframes:
            if not (0.0 <= t <= 1.0):
                raise ValueError(f"Keyframe times must be between 0.0 and 1.0, got {t}")
        self.keyframes = keyframes

    @abstractmethod
    def render(self) -> dw.DrawingElement:
        """Render the element in its initial state (static rendering)

        Returns:
            drawsvg element representing the element
        """
        if not self.keyframes:
            raise ValueError("No state, states, or keyframes set for rendering.")
        # Subclass should implement rendering logic
        pass

    @abstractmethod
    def render_at_frame_time(self, t: float) -> dw.DrawingElement:
        """Render the element at a specific animation time

        Args:
            t: Time factor from 0.0 to 1.0

        Returns:
            drawsvg element representing the element at time t
        """
        if not self.keyframes:
            raise ValueError("No state, states, or keyframes set for rendering.")
        # Subclass should implement rendering logic
        pass

    def is_animatable(self) -> bool:
        """Check if this element can be animated

        Returns:
            True if element has multiple keyframes
        """
        return len(self.keyframes) > 1

    def _get_state_at_time(self, t: float) -> State:
        """Get the interpolated state at a specific time

        Args:
            t: Time factor from 0.0 to 1.0

        Returns:
            Interpolated State at time t
        """
        # Clamp t to valid range
        t = max(0.0, min(1.0, t))

        # Handle static rendering (t == 0.0) or single keyframe
        if t == 0.0 or len(self.keyframes) == 1:
            return self.keyframes[0][1]

        # Find the two keyframes to interpolate between
        for i in range(len(self.keyframes) - 1):
            t1, state1 = self.keyframes[i]
            t2, state2 = self.keyframes[i + 1]

            if t1 <= t <= t2:
                # Found the right segment
                if t1 == t2:  # Same time (shouldn't happen with valid keyframes)
                    return state1

                # Calculate segment progress
                segment_t = (t - t1) / (t2 - t1)

                # Create interpolated state
                interpolated_state = self._create_eased_state(state1, state2, segment_t)
                return interpolated_state

        # If we get here, t is beyond the last keyframe
        return self.keyframes[-1][1]

    def _create_eased_state(
        self, start_state: State, end_state: State, t: float
    ) -> State:
        """Create an interpolated state using per-property easing functions

        Args:
            start_state: Starting state
            end_state: Ending state
            t: Time factor from 0.0 to 1.0

        Returns:
            New state with interpolated values using appropriate easing per property
        """
        # Get the default easing functions from the state class
        default_easing = getattr(start_state, "DEFAULT_EASING", {})

        # Start with the start state values
        interpolated_values = {}

        # Interpolate each field
        for field in fields(start_state):
            field_name = field.name
            start_value = getattr(start_state, field_name)
            end_value = getattr(end_state, field_name)

            # Skip if values are the same (no animation needed)
            if start_value == end_value:
                interpolated_values[field_name] = start_value
                continue

            # Get the easing function for this property
            easing_func = self.easing_overrides.get(
                field_name, default_easing.get(field_name)
            )

            # Apply easing to time parameter
            if easing_func:
                eased_t = easing_func(t)
            else:
                eased_t = t  # Default to linear if no easing function specified

            # Interpolate the value using the eased time
            if isinstance(start_value, tuple) and len(start_value) == 3:
                # Color interpolation
                interpolated_values[field_name] = Interpolation.color(
                    start_value, end_value, eased_t
                )
            elif isinstance(start_value, (int, float)):
                # Numeric interpolation
                interpolated_values[field_name] = Interpolation.lerp(
                    start_value, end_value, eased_t
                )
            else:
                # For non-numeric values, just switch at t=0.5 (stepped animation)
                interpolated_values[field_name] = (
                    start_value if eased_t < 0.5 else end_value
                )

        # Create new state with interpolated values
        return replace(start_state, **interpolated_values)
