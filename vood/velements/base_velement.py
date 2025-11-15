"""Base element class with shared keystate animation logic"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Callable, Dict, Any
from dataclasses import replace

import drawsvg as dw

from vood.components import State
from vood.transitions import interpolation

# Import the extracted modules
from vood.velements.keystate_parser import (
    parse_element_keystates,
    parse_property_keystates,
    FlexibleKeystateInput,
    SegmentKeystateTuple,
    PropertyKeyframeTuple,
    PropertyTimelineConfig,
)
from vood.transitions.easing_resolver import EasingResolver
from vood.transitions.interpolation_engine import InterpolationEngine


class BaseVElement(ABC):
    """
    Abstract base class for all animatable elements.

    Provides shared keystate animation logic using a flexible, layered easing
    priority system and supporting custom property timelines.

    Architecture:
    - KeystateParser: Handles parsing and time distribution
    - EasingResolver: Manages 4-level easing priority system
    - InterpolationEngine: Handles state and value interpolation
    """

    def __init__(
        self,
        state: Optional[State] = None,
        keystates: Optional[Iterable[FlexibleKeystateInput]] = None,
        property_easing: Optional[Dict[str, Callable[[float], float]]] = None,
        property_keystates: Optional[Dict[str, List[PropertyKeyframeTuple]]] = None,
    ) -> None:
        """
        Initialize keystate animation system.

        Args:
            state: Single static state (mutually exclusive with keystates)
            keystates: List of states with optional timing/easing
            property_easing: Instance-level easing overrides for properties
            property_keystates: Custom timelines for individual properties
        """
        # Input validation for mutual exclusivity
        provided_inputs = [arg for arg in [state, keystates] if arg is not None]
        count = len(provided_inputs)

        if count == 0:
            raise ValueError(
                "VElement requires configuration: provide 'state' or 'keystates'."
            )
        if count > 1:
            raise ValueError(
                f"Conflicting inputs provided ({count} specified). "
                "Please specify only one of 'state' or 'keystates'."
            )

        # Initialize helper systems
        self.easing_resolver = EasingResolver(property_easing)
        self.interpolation_engine = InterpolationEngine(self.easing_resolver)

        # Store property keystates (will be parsed on first use)
        self.property_keystates_raw = property_keystates or {}
        self.property_keystates: Dict[str, List[PropertyKeyframeTuple]] = {}
        self.keystates: List[SegmentKeystateTuple] = []

        # Parse and set keystates
        if state is not None:
            if isinstance(state, Iterable):
                raise ValueError("state must be a single State instance, not a list")
            self.set_state(state)
        elif keystates is not None:
            self.set_keystates(keystates)

        # Parse property keystates if provided
        if self.property_keystates_raw:
            self._parse_property_keystates()

    def set_state(self, state: State) -> None:
        """Set a single static state"""
        self.keystates = [(0.0, state, None)]

    def set_keystates(self, keystates: List[FlexibleKeystateInput]) -> None:
        """Set keystates using the flexible combined format"""
        if not keystates:
            raise ValueError("keystates cannot be empty")

        self.keystates = parse_element_keystates(keystates)

        if not self.keystates:
            raise ValueError("Keystates list could not be parsed.")
        
        self._preprocess_morph_segments()

    def _parse_property_keystates(self) -> None:
        """Parse raw property keystates into normalized format"""
        for field_name, timeline in self.property_keystates_raw.items():
            if not timeline:
                raise ValueError(f"Empty timeline for property '{field_name}'")
            self.property_keystates[field_name] = parse_property_keystates(timeline)

    @abstractmethod
    def render(self) -> Optional[dw.DrawingElement]:
        """Render the element in its initial state (static rendering)"""
        if not self.keystates:
            raise ValueError("No state, states, or keystates set for rendering.")
        pass

    @abstractmethod
    def render_at_frame_time(self, t: float) -> Optional[dw.DrawingElement]:
        """Render the element at a specific animation time"""
        if not self.keystates:
            raise ValueError("No state, states, or keystates set for rendering.")
        pass

    def is_animatable(self) -> bool:
        """Check if this element can be animated"""
        return len(self.keystates) > 1 or bool(self.property_keystates)

    def _get_state_at_time(self, t: float) -> Optional[State]:
        """
        Get the interpolated state at a specific time.

        Returns None if t is outside the element's keystate timeline range.
        This implements the element existence model: elements only exist
        within their defined keystate timeline.

        Args:
            t: Animation time (0.0 to 1.0)

        Returns:
            Interpolated state or None if element doesn't exist at time t
        """
        if not self.keystates:
            return None

        # Existence check: element only exists within its keystate range
        first_time = self.keystates[0][0]
        last_time = self.keystates[-1][0]

        if t < first_time or t > last_time:
            return None  # Element does not exist outside its defined keyframe range

        # Handle edge case: at first keystate or single keystate
        if t == first_time or len(self.keystates) == 1:
            base_state = self.keystates[0][1]
            return self._apply_property_timelines(base_state, t)

        # Find the segment containing time t
        for i in range(len(self.keystates) - 1):
            t1, state1, seg_easing1 = self.keystates[i]
            t2, state2, seg_easing2 = self.keystates[i + 1]

            if t1 <= t <= t2:
                # Handle coincident keystates
                if t1 == t2:
                    return self._apply_property_timelines(state2, t)

                # Interpolate between keystates
                segment_t = (t - t1) / (t2 - t1)

                interpolated_state = self.interpolation_engine.create_eased_state(
                    state1,
                    state2,
                    segment_t,
                    segment_easing_overrides=seg_easing1,
                    property_keystates_fields=set(self.property_keystates.keys()),
                )

                return self._apply_property_timelines(interpolated_state, t)

        # At or past final keystate
        final_state = self.keystates[-1][1]
        return self._apply_property_timelines(final_state, t)

    def _apply_property_timelines(self, base_state: State, t: float) -> State:
        """
        Apply custom property timeline values on top of the base state.

        Args:
            base_state: State from main keystate interpolation
            t: Current animation time

        Returns:
            State with property timeline values applied
        """
        if not self.property_keystates:
            return base_state

        updates = {}
        for field_name in self.property_keystates.keys():
            updates[field_name] = self._get_property_value_at_time(field_name, t)

        return replace(base_state, **updates)

    def _get_property_value_at_time(self, field_name: str, t: float) -> Any:
        """
        Get property value at time t from property_keystates.

        Property timelines extend their first/last values to 0.0/1.0 to ensure
        properties always have values when the element exists.

        Args:
            field_name: Name of the property
            t: Animation time

        Returns:
            Interpolated property value
        """
        timeline = self.property_keystates[field_name]

        if not timeline:
            raise ValueError(f"Empty timeline for property '{field_name}'")

        # Property timelines extend to full range
        if t <= timeline[0][0]:
            return timeline[0][1]
        if t >= timeline[-1][0]:
            return timeline[-1][1]

        # Find the segment containing time t
        for i in range(len(timeline) - 1):
            item1 = timeline[i]
            t1, val1, *rest1 = item1
            easing1 = rest1[0] if rest1 else None

            item2 = timeline[i + 1]
            t2, val2, *rest2 = item2

            if t1 <= t <= t2:
                if t1 == t2:
                    return val2

                segment_duration = t2 - t1
                segment_t = (t - t1) / segment_duration

                # Get easing function (use segment-level or fallback)
                if easing1 is None:
                    base_state = self.keystates[0][1] if self.keystates else None
                    easing_func = self.easing_resolver.get_easing_for_property_timeline(
                        base_state, field_name
                    )
                else:
                    easing_func = easing1

                eased_t = easing_func(segment_t) if easing_func else segment_t

                # Interpolate the value
                base_state = self.keystates[0][1] if self.keystates else None
                if not base_state:
                    return interpolation.lerp(val1, val2, eased_t)

                return self.interpolation_engine.interpolate_value(
                    base_state, field_name, val1, val2, eased_t
                )

        return timeline[-1][1]

    def _preprocess_morph_segments(self) -> None:
        """
        Convert MorphState segments to MorphRawState with aligned vertices.

        This happens once when keystates are set, not on every frame.
        After this, normal field-by-field interpolation works correctly.
        """
        from vood.components.states.morph_base import MorphBaseState

        for i in range(len(self.keystates) - 1):
            t1, state1, easing1 = self.keystates[i]
            t2, state2, easing2 = self.keystates[i + 1]

            # Check if this is a MorphState → MorphState segment
            if isinstance(state1, MorphBaseState) and isinstance(state2, MorphBaseState):
                from vood.transitions.interpolation.morpher.morph_state_interpolation import align_and_convert_to_raw

                # Convert both states to MorphRawState with aligned vertices
                aligned_state1 = align_and_convert_to_raw(state1, state2, is_start=True)
                aligned_state2 = align_and_convert_to_raw(
                    state1, state2, is_start=False
                )

                # Replace in the keystates list
                self.keystates[i] = (t1, aligned_state1, easing1)
                self.keystates[i + 1] = (t2, aligned_state2, easing2)
