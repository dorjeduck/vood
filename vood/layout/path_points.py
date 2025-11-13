"""Path layout state function for arbitrary paths"""

import math
from typing import List, Optional, Callable, Sequence, Tuple
from dataclasses import replace
from vood.component import State
from .enums import ElementAlignment


def path_points(
    states: List[State],
    points: Sequence[Tuple[float, float]],
    alignment: ElementAlignment = ElementAlignment.PRESERVE,
    element_rotation_offset: float = 0,
    element_rotation_offset_fn: Optional[Callable[[float], float]] = None,
    smooth: bool = True,
) -> List[State]:
    """
    Arrange states along an arbitrary path defined by points with uniform spacing.

    Positions elements at equally spaced arc-length positions along a path that
    connects the given points, ensuring uniform spacing regardless of segment length.
    Pads the path with phantom points when smoothing to ensure the full path is used.

    Args:
        states: List of states to arrange
        points: List of (x, y) tuples defining the path
        alignment: How to align each element relative to the path.
        element_rotation_offset: Additional rotation in degrees added to the alignment base.
        element_rotation_offset_fn: Function that takes position t (0-1) and returns rotation offset.
        smooth: If True, use Catmull-Rom spline interpolation for smoother curves.

    Returns:
        New list of states with positions along the path
    """
    if not states or not points or len(points) < 2:
        return []

    num_elements = len(states)

    # --- FIX: Padding points for Catmull-Rom to use full path ---
    working_points = list(points)
    if smooth and len(points) >= 2:
        p_start = working_points[0]
        p_next = working_points[1]
        p_end = working_points[-1]
        p_prev = working_points[-2]

        # Calculate start phantom point (reflect P1 across P0)
        p_phantom_start = (
            2 * p_start[0] - p_next[0],
            2 * p_start[1] - p_next[1],
        )

        # Calculate end phantom point (reflect Pn-2 across Pn-1)
        p_phantom_end = (
            2 * p_end[0] - p_prev[0],
            2 * p_end[1] - p_prev[1],
        )

        # Insert phantom points
        working_points.insert(0, p_phantom_start)
        working_points.append(p_phantom_end)

    points_to_use = working_points
    # -----------------------------------------------------------

    def get_path_length(pts: Sequence[Tuple[float, float]]) -> float:
        """Calculate total path length (used for linear segments only)"""
        total = 0.0
        for i in range(len(pts) - 1):
            dx = pts[i + 1][0] - pts[i][0]
            dy = pts[i + 1][1] - pts[i][1]
            total += math.sqrt(dx * dx + dy * dy)
        return total

    def catmull_rom_point(
        t: float,
        p0: Tuple[float, float],
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
    ) -> Tuple[float, float]:
        """Calculate point on Catmull-Rom spline"""
        t2 = t * t
        t3 = t2 * t

        x = 0.5 * (
            (2 * p1[0])
            + (-p0[0] + p2[0]) * t
            + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
            + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
        )

        y = 0.5 * (
            (2 * p1[1])
            + (-p0[1] + p2[1]) * t
            + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
            + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
        )

        return (x, y)

    def get_point_at_t(t: float) -> Tuple[float, float]:
        """Get point at normalized position t (0-1) along path based on parameter t."""
        if smooth:  # Logic relies on padded list now
            num_segments = len(points_to_use) - 3  # Catmull-Rom uses n-3 segments

            # Map global t (0-1) to local segment t and index
            segment_index = min(int(t * num_segments), num_segments - 1)
            local_t = (t * num_segments) - segment_index

            # Control points p0 to p3 are indexed relative to the padded list
            p0 = points_to_use[segment_index]
            p1 = points_to_use[segment_index + 1]
            p2 = points_to_use[segment_index + 2]
            p3 = points_to_use[segment_index + 3]

            return catmull_rom_point(local_t, p0, p1, p2, p3)
        else:
            # Linear interpolation between points_to_use (same as original points if not smooth)
            total_length = get_path_length(points_to_use)
            target_distance = t * total_length

            current_distance = 0.0
            for i in range(len(points_to_use) - 1):
                dx = points_to_use[i + 1][0] - points_to_use[i][0]
                dy = points_to_use[i + 1][1] - points_to_use[i][1]
                segment_length = math.sqrt(dx * dx + dy * dy)

                if current_distance + segment_length >= target_distance:
                    # Point is in this segment
                    segment_t = (
                        (target_distance - current_distance) / segment_length
                        if segment_length > 0
                        else 0
                    )
                    x = points_to_use[i][0] + dx * segment_t
                    y = points_to_use[i][1] + dy * segment_t
                    return (x, y)

                current_distance += segment_length

            return points_to_use[-1]

    def get_tangent_angle(t: float) -> float:
        """Get tangent angle at position t using finite difference."""
        dt = 0.001
        t1 = max(0, t - dt)
        t2 = min(1, t + dt)

        p1 = get_point_at_t(t1)
        p2 = get_point_at_t(t2)

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        return math.degrees(math.atan2(dy, dx))

    # --- ARC-LENGTH PARAMETERIZATION IMPLEMENTATION ---
    def resample_path(samples: int = 1000) -> Tuple[List[float], List[float]]:
        """
        Pre-calculate a map (distance_t_map, t_map) for arc-length parameterization.
        """
        distance_t_map = [0.0]
        t_map = [0.0]

        total_length = 0.0
        last_point = get_point_at_t(0.0)

        for i in range(1, samples + 1):
            t = i / samples
            current_point = get_point_at_t(t)

            dx = current_point[0] - last_point[0]
            dy = current_point[1] - last_point[1]
            segment_length = math.sqrt(dx * dx + dy * dy)
            total_length += segment_length

            distance_t_map.append(total_length)
            t_map.append(t)
            last_point = current_point

        if total_length == 0:
            return ([0.0] * (samples + 1), t_map)

        normalized_distance_t_map = [d / total_length for d in distance_t_map]

        return (normalized_distance_t_map, t_map)

    # Pre-calculate the arc length parameterization map
    normalized_distance_t_map, t_map = resample_path(samples=1000)
    # --------------------------------------------------

    result = []
    for i, state in enumerate(states):
        # 1. Calculate the target normalized distance (0 to 1) for the element
        target_distance = i / (num_elements - 1) if num_elements > 1 else 0

        # 2. Find the 't' that corresponds to the target distance by interpolating the map
        new_t = 0.0
        for j in range(len(normalized_distance_t_map) - 1):
            d1 = normalized_distance_t_map[j]
            d2 = normalized_distance_t_map[j + 1]

            if d1 <= target_distance <= d2:
                t1 = t_map[j]
                t2 = t_map[j + 1]

                segment_dist = d2 - d1
                if segment_dist > 0:
                    local_t_factor = (target_distance - d1) / segment_dist
                    new_t = t1 + local_t_factor * (t2 - t1)
                else:
                    new_t = t1
                break

        t = new_t

        x, y = get_point_at_t(t)
        tangent_angle = get_tangent_angle(t)

        additional_rotation = (
            element_rotation_offset_fn(t)
            if element_rotation_offset_fn
            else element_rotation_offset
        )

        # Element alignment logic
        if alignment == ElementAlignment.PRESERVE:
            element_angle = state.rotation
        elif alignment == ElementAlignment.LAYOUT:
            element_angle = tangent_angle + additional_rotation
        elif alignment == ElementAlignment.UPRIGHT:
            element_angle = additional_rotation
        else:
            element_angle = state.rotation

        new_state = replace(state, x=x, y=y, rotation=element_angle)
        result.append(new_state)

    return result
