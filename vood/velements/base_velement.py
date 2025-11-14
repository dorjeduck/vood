"""Base element class with shared keystate animation logic"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Tuple, Callable, Dict, Any, Union
from dataclasses import fields, replace

import drawsvg as dw

from vood.components import State
from vood.components.states.path import MorphMethod
from vood.paths import SVGPath
from vood.transitions import interpolation
from vood.transitions.interpolation import NativeMorpher, FlubberMorpher
from vood.transitions import easing
from vood.core.color import Color

# Define the primary keystate types
# Main keystates (normalized): (time, state, optional_segment_easing_dict)
SegmentKeystateTuple = Tuple[
    float, State, Optional[Dict[str, Callable[[float], float]]]
]
# Property timelines: (time, value, optional_easing_function)
PropertyKeyframeTuple = Tuple[float, Any, Optional[Callable[[float], float]]]
PropertyTimelineConfig = Dict[str, List[PropertyKeyframeTuple]]

# New flexible type for user input, combining states and time anchors
FlexibleKeystateInput = Union[
    State,
    Tuple[float, State],  # (time, state)
    Tuple[State, Optional[Dict[str, Callable[[float], float]]]],  # (state, easing_dict)
    SegmentKeystateTuple,  # (time, state, easing_dict)
]


class BaseVElement(ABC):
    """Abstract base class for all animatable elements

    Provides shared keystate animation logic using a flexible, layered easing
    priority system and supporting custom property timelines.
    """

    def __init__(
        self,
        state: Optional[State] = None,
        keystates: Optional[Iterable[FlexibleKeystateInput]] = None,
        # Level 2 easing override
        instance_easing: Optional[Dict[str, Callable[[float], float]]] = None,
        # Level 4 control: custom property timelines
        property_timelines: Optional[PropertyTimelineConfig] = None,
    ) -> None:
        """Initialize keystate animation system"""

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

        self.instance_easing = instance_easing or {}
        self.property_timelines = property_timelines or {}
        self.keystates: List[SegmentKeystateTuple] = []

        if state is not None:
            if isinstance(state, Iterable):
                raise ValueError("state must be a single State instance, not a list")
            self.set_state(state)
        elif keystates is not None:
            self.set_keystates(keystates)

    def set_state(self, state: State) -> None:
        """Set a single static state"""
        self.keystates = [(0.0, state, None)]

    def set_keystates(self, keystates: List[FlexibleKeystateInput]) -> None:
        """Set keystates using the flexible combined format, calculating implicit times."""
        if not keystates:
            raise ValueError("keystates cannot be empty")

        self.keystates = self._parse_flexible_keystates(keystates)

        if not self.keystates:
            raise ValueError("Keystates list could not be parsed.")

    def _parse_flexible_keystates(
        self, flexible_list: List[FlexibleKeystateInput]
    ) -> List[SegmentKeystateTuple]:
        """
        Parses a mixed list of States and KeystateTuples into a normalized, time-stamped list.
        Conditionally enforces 0.0/1.0 boundaries based on whether explicit times were provided.
        """

        # 1. First Pass: Identify and normalize all items, mark explicit times
        normalized_keystates: List[
            Tuple[Optional[float], State, Optional[Dict[str, Callable]]]
        ] = []
        has_explicit_times = False

        for item in flexible_list:
            t: Optional[float] = None
            state: State
            easing_dict: Optional[Dict] = None

            if isinstance(item, State):
                state = item
            elif isinstance(item, tuple):
                if len(item) == 2:
                    if isinstance(item[0], float) or isinstance(item[0], int):
                        t = float(item[0])
                        state = item[1]
                        has_explicit_times = True
                    elif isinstance(item[0], State):
                        state = item[0]
                        easing_dict = item[1]
                    else:
                        raise ValueError(f"Invalid 2-element keystate format: {item}")
                elif len(item) == 3:
                    t = float(item[0])
                    state = item[1]
                    easing_dict = item[2]
                    has_explicit_times = True
                else:
                    raise ValueError(
                        f"Keystate tuple length must be 1, 2, or 3, got {len(item)}"
                    )
            else:
                raise ValueError(f"Invalid keystate item type: {type(item)}")

            if t is not None:
                if not (0.0 <= t <= 1.0):
                    raise ValueError(
                        f"Keystate time must be between 0.0 and 1.0, got {t}"
                    )
                has_explicit_times = True  # Redundant, but ensures safety

            normalized_keystates.append((t, state, easing_dict))

        if not normalized_keystates:
            return []

        # 2. Conditional Boundary Enforcement (The Fix)
        if not has_explicit_times or (
            len(normalized_keystates) == 1 and normalized_keystates[0][0] is None
        ):
            # Case: Pure [S1, S2, S3] input (old set_states behavior)
            # Enforce 0.0 and 1.0 anchors to span the full timeline
            if normalized_keystates[0][0] is None:
                normalized_keystates[0] = (
                    0.0,
                    normalized_keystates[0][1],
                    normalized_keystates[0][2],
                )
            if normalized_keystates[-1][0] is None:
                normalized_keystates[-1] = (
                    1.0,
                    normalized_keystates[-1][1],
                    normalized_keystates[-1][2],
                )

        # 3. Calculate Implicit Times
        final_keystates: List[SegmentKeystateTuple] = []

        # Find the first explicit anchor to start the process
        i = 0
        while i < len(normalized_keystates) and normalized_keystates[i][0] is None:
            # If the list starts with implicit times, those must fall to the first
            # explicit time, but for Vood's existence logic, we assume the first
            # keyframe is the start of existence, so we use the first defined time.
            # If the list starts with [S1, (0.5, S2)], S1 must be assigned t=0.0
            # IF the first explicit time is also 0.0, which is handled below.
            i += 1

        # Ensure the very first keystate has a time anchor (this handles [S1, (0.5, S2)])
        if normalized_keystates[0][0] is None:
            first_explicit_t = (
                normalized_keystates[i][0] if i < len(normalized_keystates) else 0.0
            )
            # If the first item is implicit, its time is the same as the next explicit time
            # UNLESS it's the 0.0 enforced case above, which sets the time to 0.0.
            normalized_keystates[0] = (
                first_explicit_t,
                normalized_keystates[0][1],
                normalized_keystates[0][2],
            )

        i = 0
        while i < len(normalized_keystates):
            t_start, state_start, easing_dict_start = normalized_keystates[i]

            # Find the next explicit time anchor (j)
            j = i + 1
            while j < len(normalized_keystates) and normalized_keystates[j][0] is None:
                j += 1

            # Get the end anchor time
            t_end = (
                normalized_keystates[j][0] if j < len(normalized_keystates) else t_start
            )

            # Number of gaps/segments between i and j (inclusive of both anchors)
            num_gaps = j - i
            duration = t_end - t_start

            if num_gaps > 0:
                step = duration / num_gaps
            else:
                step = 0

            # Generate keyframes for the segment [i...j]
            for k in range(num_gaps + 1):
                item_index = i + k
                if item_index >= len(normalized_keystates):
                    break

                t_current, state_current, easing_dict_current = normalized_keystates[
                    item_index
                ]

                # Calculate time for implicit keys
                final_t = t_start + k * step if t_current is None else t_current

                # Correct rounding errors
                if k == num_gaps:
                    final_t = t_end

                final_keystates.append((final_t, state_current, easing_dict_current))

            # Move index to the next anchor point
            i = j

        # 4. Deduplicate and Final Sort
        unique_keystates: List[SegmentKeystateTuple] = []
        last_t = -1.0

        final_keystates.sort(key=lambda x: x[0])

        for t, state, easing_dict in final_keystates:
            if t > last_t:
                unique_keystates.append((t, state, easing_dict))
                last_t = t
            elif t == last_t:
                # Replace the previous entry at the same time for the last defined state/easing
                unique_keystates[-1] = (t, state, easing_dict)

        return unique_keystates

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
        return len(self.keystates) > 1 or bool(self.property_timelines)

    def _get_property_value_at_time(self, field_name: str, t: float) -> Any:
        # ... (rest of _get_property_value_at_time remains unchanged)
        timeline = self.property_timelines[field_name]

        if t <= timeline[0][0]:
            return timeline[0][1]
        if t >= timeline[-1][0]:
            return timeline[-1][1]

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

                if easing1 is None:
                    easing_func = self._get_easing_for_field_fallback(field_name)
                else:
                    easing_func = easing1

                eased_t = easing_func(segment_t) if easing_func else segment_t

                base_state = self.keystates[0][1] if self.keystates else None
                if not base_state:
                    return interpolation.lerp(val1, val2, eased_t)

                return self._interpolate_value(
                    base_state, field_name, val1, val2, eased_t
                )

        return timeline[-1][1]

    def _get_easing_for_field_fallback(
        self, field_name: str
    ) -> Callable[[float], float]:
        """Gets the fallback easing (Instance or State Class default) for custom property timelines"""

        if not self.keystates:
            return easing.linear

        state = self.keystates[0][1]

        if field_name in self.instance_easing:
            return self.instance_easing[field_name]

        default_easing = getattr(state, "DEFAULT_EASING", {})
        if field_name in default_easing:
            return default_easing[field_name]

        return easing.linear

    def _get_state_at_time(self, t: float) -> Optional[State]:
        """Get the interpolated state at a specific time"""
        if not self.keystates:
            return None

        # --- EXISTENCE CHECK (Restored Logic) ---
        first_time = self.keystates[0][0]
        last_time = self.keystates[-1][0]

        if t < first_time or t > last_time:
            return None  # Element does not exist outside its defined keyframe range
        # ---------------------------------------

        if t == first_time or len(self.keystates) == 1:
            base_state = self.keystates[0][1]
            return self._apply_property_timelines(base_state, t)

        for i in range(len(self.keystates) - 1):
            t1, state1, seg_easing1 = self.keystates[i]
            t2, state2, seg_easing2 = self.keystates[i + 1]

            if t1 <= t <= t2:
                if t1 == t2:
                    return self._apply_property_timelines(state2, t)

                segment_t = (t - t1) / (t2 - t1)

                interpolated_state = self._create_eased_state(
                    state1, state2, segment_t, segment_easing_overrides=seg_easing1
                )

                return self._apply_property_timelines(interpolated_state, t)

        final_state = self.keystates[-1][1]
        return self._apply_property_timelines(final_state, t)

    def _apply_property_timelines(self, base_state: State, t: float) -> State:
        """Applies values from custom property_timelines on top of the base state."""
        if not self.property_timelines:
            return base_state

        updates = {}
        for field_name in self.property_timelines.keys():
            updates[field_name] = self._get_property_value_at_time(field_name, t)

        return replace(base_state, **updates)

    def _create_eased_state(
        self,
        start_state: State,
        end_state: State,
        t: float,
        segment_easing_overrides: Optional[Dict[str, Callable[[float], float]]],
    ) -> State:
        """Create an interpolated state from main keystates (ignoring fields in property_timelines)"""
        interpolated_values = {}

        for field in fields(start_state):
            field_name = field.name

            if field_name in self.property_timelines:
                continue

            start_value = getattr(start_state, field_name)
            end_value = getattr(end_state, field_name)

            if start_value == end_value:
                interpolated_values[field_name] = start_value
                continue

            easing_func = self._get_easing_for_field(
                start_state, field_name, segment_easing_overrides
            )
            eased_t = easing_func(t) if easing_func else t

            interpolated_values[field_name] = self._interpolate_value(
                start_state, field_name, start_value, end_value, eased_t
            )

        return replace(start_state, **interpolated_values)

    def _get_easing_for_field(
        self,
        start_state: State,
        field_name: str,
        segment_easing_overrides: Optional[Dict[str, Callable[[float], float]]],
    ) -> Optional[Callable[[float], float]]:
        """Get the easing function for a field with 4-level priority"""

        if (
            segment_easing_overrides is not None
            and field_name in segment_easing_overrides
        ):
            return segment_easing_overrides[field_name]

        if field_name in self.instance_easing:
            return self.instance_easing[field_name]

        default_easing = getattr(start_state, "DEFAULT_EASING", {})
        if field_name in default_easing:
            return default_easing[field_name]

        return easing.linear

    def _interpolate_value(
        self,
        state: State,
        field_name: str,
        start_value: Any,
        end_value: Any,
        eased_t: float,
    ) -> Any:
        """Interpolate a single value based on its type and field context (Requires Color objects)"""

        # 1. SVG Path interpolation
        if isinstance(start_value, SVGPath):
            return self._interpolate_path(state, start_value, end_value, eased_t)

        # 2. Color interpolation (User must provide Color objects)
        if isinstance(start_value, Color):
            return start_value.interpolate(end_value, eased_t)

        # 3. Angle interpolation
        if self._is_angle_field(state, field_name):
            return interpolation.angle(start_value, end_value, eased_t)

        # 4. Numeric interpolation
        if isinstance(start_value, (int, float)):
            return interpolation.lerp(start_value, end_value, eased_t)

        # 5. Non-numeric values: step at t=0.5
        return interpolation.step(start_value, end_value, eased_t)

    def _interpolate_path(
        self, state: State, start_path: SVGPath, end_path: SVGPath, eased_t: float
    ) -> SVGPath:
        morph_method = getattr(state, "morph_method", None)
        if morph_method == MorphMethod.SHAPE or morph_method == "shape":
            return FlubberMorpher.for_paths(start_path, end_path)(eased_t)
        if morph_method == MorphMethod.STROKE or morph_method == "stroke":
            return NativeMorpher.for_paths(start_path, end_path)(eased_t)
        if self._path_is_closed(start_path):
            return FlubberMorpher.for_paths(start_path, end_path)(eased_t)
        else:
            return NativeMorpher.for_paths(start_path, end_path)(eased_t)

    def _is_angle_field(self, state: State, field_name: str) -> bool:
        if not hasattr(state, "is_angle"):
            return False
        field_obj = next((f for f in fields(state) if f.name == field_name), None)
        if field_obj:
            return state.is_angle(field_obj)
        return False

    def _path_is_closed(self, path: SVGPath, tolerance: float = 0.01) -> bool:
        path_str = path.to_string().strip().upper()
        if path_str.endswith("Z"):
            return True
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
