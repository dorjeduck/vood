"""Keystate parsing utilities for element and property timelines"""

from typing import List, Optional, Tuple, Callable, Dict, Any, Union

from vood.components import State

# Type definitions
SegmentKeystateTuple = Tuple[
    float, State, Optional[Dict[str, Callable[[float], float]]]
]

PropertyKeyframeTuple = Tuple[float, Any, Optional[Callable[[float], float]]]

PropertyTimelineConfig = Dict[str, List[PropertyKeyframeTuple]]

FlexibleKeystateInput = Union[
    State,
    Tuple[float, State],  # (time, state)
    Tuple[State, Optional[Dict[str, Callable[[float], float]]]],  # (state, easing_dict)
    SegmentKeystateTuple,  # (time, state, easing_dict)
]


def parse_element_keystates(
    flexible_list: List[FlexibleKeystateInput],
) -> List[SegmentKeystateTuple]:
    """
    Parse element-level keystates with flexible time anchoring.

    Rules:
    - States without times are distributed evenly between explicit time anchors
    - If NO explicit times provided: first anchors to 0.0, last to 1.0 (full timeline)
    - If ANY explicit times provided: respects those boundaries (partial timeline allowed)

    Examples:
        [S1, S2, S3] -> [(0.0, S1), (0.5, S2), (1.0, S3)]
        [(0.2, S1), S2, (0.8, S3)] -> [(0.2, S1), (0.5, S2), (0.8, S3)]
        [S1, (0.5, S2), S3] -> [(0.0, S1), (0.5, S2), (1.0, S3)]
    """
    if not flexible_list:
        raise ValueError("keystates cannot be empty")

    # Step 1: Normalize input format and track explicit times
    normalized, has_explicit_times = _normalize_keystates(flexible_list)

    # Step 2: Apply boundary rules for pure implicit input
    if not has_explicit_times:
        normalized = _apply_full_timeline_boundaries(normalized)

    # Step 3: Distribute implicit times between anchors
    timestamped = _distribute_implicit_times(normalized)

    # Step 4: Sort and deduplicate
    return _finalize_keystates(timestamped)


def parse_property_keystates(
    flexible_list: List[Union[Any, PropertyKeyframeTuple]],
) -> List[PropertyKeyframeTuple]:
    """
    Parse property-level keystates with mandatory full timeline coverage.

    Rules:
    - Values without times are distributed evenly between explicit time anchors
    - ALWAYS extends to cover 0.0-1.0 range (properties exist when element exists)

    The extension happens by:
    1. Adding explicit 0.0 anchor if needed (uses first value)
    2. Adding explicit 1.0 anchor if needed (uses last value)

    Examples:
        [(0.3, val1), (0.7, val2)] -> [(0.0, val1), (0.3, val1), (0.7, val2), (1.0, val2)]
        [val1, val2] -> [(0.0, val1), (1.0, val2)]
        [val1, (0.5, val2), val3] -> [(0.0, val1), (0.5, val2), (1.0, val3)]
    """
    if not flexible_list:
        raise ValueError("property keystates cannot be empty")

    # Step 1: Normalize to (time, value, easing) format
    normalized = []
    has_explicit_times = False

    for item in flexible_list:
        t: Optional[float] = None
        val: Any
        easing: Optional[Callable] = None

        # Handle bare values (not tuples)
        if not isinstance(item, tuple):
            val = item
        elif len(item) == 2:
            # Could be (time, value) or (value, easing) - check first element type
            if isinstance(item[0], (float, int)) and 0.0 <= float(item[0]) <= 1.0:
                t = float(item[0])
                val = item[1]
                has_explicit_times = True
            else:
                # Treat as (value, easing)
                val = item[0]
                easing = item[1]
        elif len(item) == 3:
            t = float(item[0])
            val = item[1]
            easing = item[2]
            if not (0.0 <= t <= 1.0):
                raise ValueError(f"Property time must be between 0.0 and 1.0, got {t}")
            has_explicit_times = True
        else:
            raise ValueError(
                f"Property keyframe must be 1, 2 or 3 elements, got {len(item)}"
            )

        if t is not None and not (0.0 <= t <= 1.0):
            raise ValueError(f"Property time must be between 0.0 and 1.0, got {t}")

        normalized.append((t, val, easing))

    # Step 2: ALWAYS apply full timeline boundaries for properties
    if normalized[0][0] is None or normalized[0][0] > 0.0:
        # Extend first value to 0.0
        first_val = normalized[0][1]
        first_easing = normalized[0][2]
        normalized.insert(0, (0.0, first_val, first_easing))

    if normalized[-1][0] is None or normalized[-1][0] < 1.0:
        # Extend last value to 1.0
        last_val = normalized[-1][1]
        last_easing = normalized[-1][2]
        # Only add if not already at 1.0
        if normalized[-1][0] != 1.0:
            normalized.append((1.0, last_val, last_easing))

    # Step 3: Distribute implicit times
    timestamped = _distribute_implicit_times_property(normalized)

    # Step 4: Sort and deduplicate
    return _finalize_property_keystates(timestamped)


# Private helper functions


def _normalize_keystates(
    flexible_list: List[FlexibleKeystateInput],
) -> Tuple[List[Tuple[Optional[float], State, Optional[Dict]]], bool]:
    """
    Normalize flexible input into (time, state, easing_dict) tuples.
    Returns (normalized_list, has_explicit_times)
    """
    normalized = []
    has_explicit_times = False

    for item in flexible_list:
        t: Optional[float] = None
        state: State
        easing_dict: Optional[Dict] = None

        if isinstance(item, State):
            state = item
        elif isinstance(item, tuple):
            if len(item) == 2:
                if isinstance(item[0], (float, int)):
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
                    f"Keystate tuple length must be 2 or 3, got {len(item)}"
                )
        else:
            raise ValueError(f"Invalid keystate item type: {type(item)}")

        if t is not None and not (0.0 <= t <= 1.0):
            raise ValueError(f"Keystate time must be between 0.0 and 1.0, got {t}")

        normalized.append((t, state, easing_dict))

    return normalized, has_explicit_times


def _apply_full_timeline_boundaries(
    normalized: List[Tuple[Optional[float], State, Optional[Dict]]],
) -> List[Tuple[Optional[float], State, Optional[Dict]]]:
    """Apply 0.0 and 1.0 boundaries when no explicit times provided"""
    if not normalized:
        return normalized

    # Anchor first to 0.0
    normalized[0] = (0.0, normalized[0][1], normalized[0][2])

    # Anchor last to 1.0 (if more than one keystate)
    if len(normalized) > 1:
        normalized[-1] = (1.0, normalized[-1][1], normalized[-1][2])

    return normalized


def _distribute_implicit_times(
    normalized: List[Tuple[Optional[float], State, Optional[Dict]]],
) -> List[SegmentKeystateTuple]:
    """Distribute implicit times evenly between explicit time anchors"""
    if not normalized:
        return []

    final_keystates = []
    i = 0

    while i < len(normalized):
        t_current, state_current, easing_dict_current = normalized[i]

        # If explicit time, add it and continue
        if t_current is not None:
            final_keystates.append((t_current, state_current, easing_dict_current))
            i += 1
            continue

        # Find previous anchor (or use 0.0 as default)
        t_prev = final_keystates[-1][0] if final_keystates else 0.0

        # Find next explicit anchor
        j = i
        while j < len(normalized) and normalized[j][0] is None:
            j += 1

        t_next = normalized[j][0] if j < len(normalized) else 1.0

        # Distribute implicit keystates evenly between anchors
        num_implicit = j - i
        for k in range(num_implicit):
            idx = i + k
            t_interpolated = t_prev + (t_next - t_prev) * (k + 1) / (num_implicit + 1)
            _, state_k, easing_dict_k = normalized[idx]
            final_keystates.append((t_interpolated, state_k, easing_dict_k))

        i = j

    return final_keystates


def _distribute_implicit_times_property(
    normalized: List[Tuple[Optional[float], Any, Optional[Callable]]],
) -> List[PropertyKeyframeTuple]:
    """Distribute implicit times for property keystates"""
    if not normalized:
        return []

    final_keystates = []
    i = 0

    while i < len(normalized):
        t_current, val_current, easing_current = normalized[i]

        # If explicit time, add it and continue
        if t_current is not None:
            final_keystates.append((t_current, val_current, easing_current))
            i += 1
            continue

        # Find previous anchor
        t_prev = final_keystates[-1][0] if final_keystates else 0.0

        # Find next explicit anchor
        j = i
        while j < len(normalized) and normalized[j][0] is None:
            j += 1

        t_next = normalized[j][0] if j < len(normalized) else 1.0

        # Distribute implicit keystates evenly
        num_implicit = j - i
        for k in range(num_implicit):
            idx = i + k
            t_interpolated = t_prev + (t_next - t_prev) * (k + 1) / (num_implicit + 1)
            _, val_k, easing_k = normalized[idx]
            final_keystates.append((t_interpolated, val_k, easing_k))

        i = j

    return final_keystates


def _finalize_keystates(
    keystates: List[SegmentKeystateTuple],
) -> List[SegmentKeystateTuple]:
    """Sort and deduplicate keystates"""
    keystates.sort(key=lambda x: x[0])

    unique_keystates = []
    for t, state, easing_dict in keystates:
        if not unique_keystates or t > unique_keystates[-1][0]:
            unique_keystates.append((t, state, easing_dict))
        elif t == unique_keystates[-1][0]:
            # Replace with last definition at same time
            unique_keystates[-1] = (t, state, easing_dict)

    return unique_keystates


def _finalize_property_keystates(
    keystates: List[PropertyKeyframeTuple],
) -> List[PropertyKeyframeTuple]:
    """Sort and deduplicate property keystates"""
    keystates.sort(key=lambda x: x[0])

    unique_keystates = []
    for t, val, easing in keystates:
        if not unique_keystates or t > unique_keystates[-1][0]:
            unique_keystates.append((t, val, easing))
        elif t == unique_keystates[-1][0]:
            # Replace with last definition at same time
            unique_keystates[-1] = (t, val, easing)

    return unique_keystates
