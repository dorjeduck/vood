from __future__ import annotations
import math
from dataclasses import fields
from typing import List, Tuple

from vood.components.states.morph_base import MorphBaseState, MorphRawState


def centroid(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculate the centroid of vertices"""
    if not vertices:
        return (0.0, 0.0)
    n = len(vertices)
    cx = sum(x for x, y in vertices) / n
    cy = sum(y for x, y in vertices) / n
    return cx, cy


def angle_from_centroid(
    vertex: Tuple[float, float], center: Tuple[float, float]
) -> float:
    """Calculate angle of vertex from centroid in Vood coordinates

    Vood uses: 0° = North (up), 90° = East (right), clockwise
    """
    dx = vertex[0] - center[0]
    dy = vertex[1] - center[1]

    # Convert to Vood coordinate system
    angle = math.atan2(dx, -dy)

    # Normalize to 0-2π range
    if angle < 0:
        angle += 2 * math.pi

    return angle


def angle_distance(a1: float, a2: float) -> float:
    """Calculate shortest angular distance between two angles"""
    diff = (a2 - a1) % (2 * math.pi)
    if diff > math.pi:
        diff = 2 * math.pi - diff
    return diff


def rotate_vertices(
    vertices: List[Tuple[float, float]], rotation_degrees: float
) -> List[Tuple[float, float]]:
    """Rotate vertices by given angle"""
    if rotation_degrees == 0:
        return vertices

    angle_rad = math.radians(rotation_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    return [(x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in vertices]


def align_vertices(
    verts1: List[Tuple[float, float]],
    verts2: List[Tuple[float, float]],
    rotation1: float = 0,
    rotation2: float = 0,
) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    """Align two vertex lists for optimal morphing

    Takes rotation into account when calculating angular positions.
    Returns aligned original (un-rotated) vertices.
    """
    if len(verts1) != len(verts2):
        raise ValueError(
            f"Vertex lists must have same length: {len(verts1)} != {len(verts2)}"
        )

    if not verts1 or not verts2:
        return verts1, verts2

    # Apply shape rotations for alignment calculation
    verts1_rotated = rotate_vertices(verts1, rotation1)
    verts2_rotated = rotate_vertices(verts2, rotation2)

    # Calculate centroids
    c1 = centroid(verts1_rotated)
    c2 = centroid(verts2_rotated)

    # Get angular positions from centroids
    angles1 = [angle_from_centroid(v, c1) for v in verts1_rotated]
    angles2 = [angle_from_centroid(v, c2) for v in verts2_rotated]

    # Find rotation offset that minimizes total angular distance
    n = len(verts2)
    best_offset = 0
    min_distance = float("inf")

    for offset in range(n):
        total_dist = sum(
            angle_distance(angles1[i], angles2[(i + offset) % n]) for i in range(n)
        )

        if total_dist < min_distance:
            min_distance = total_dist
            best_offset = offset

    # Rotate original vertices by best_offset
    verts2_aligned = verts2[best_offset:] + verts2[:best_offset]

    return verts1, verts2_aligned


def align_and_convert_to_raw(
    state1: MorphBaseState, state2: MorphBaseState, is_start: bool
) -> MorphRawState:
    """Convert a MorphState to MorphRawState with aligned vertices

    This is called once per segment during keystate preprocessing.

    Args:
        state1: First state in the transition
        state2: Second state in the transition
        is_start: True if converting state1, False if converting state2

    Returns:
        MorphRawState with aligned vertices and all other fields copied
    """
    if state1.num_points != state2.num_points:
        raise ValueError(
            f"Cannot morph shapes with different num_points: "
            f"{state1.num_points} != {state2.num_points}"
        )

    # Get raw vertices
    verts1 = state1.get_vertices()
    verts2 = state2.get_vertices()

    # Align vertices accounting for rotation
    verts1_aligned, verts2_aligned = align_vertices(
        verts1, verts2, rotation1=state1.rotation, rotation2=state2.rotation
    )

    # Choose which state to convert
    source_state = state1 if is_start else state2
    aligned_verts = verts1_aligned if is_start else verts2_aligned

    # Copy all fields from source state
    field_values = {}
    for field in fields(source_state):
        field_values[field.name] = getattr(source_state, field.name)

    # Create MorphRawState with aligned vertices
    return MorphRawState(vertices=aligned_verts, **field_values)
