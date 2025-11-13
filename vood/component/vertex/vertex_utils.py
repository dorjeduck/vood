"""Utility functions for vertex operations"""

from __future__ import annotations
import math
from typing import List, Tuple


def centroid(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculate the centroid (center of mass) of a set of vertices

    Args:
        vertices: List of (x, y) tuples

    Returns:
        (cx, cy) centroid position
    """
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

    Args:
        vertex: (x, y) position
        center: (cx, cy) centroid position

    Returns:
        Angle in radians (0 to 2π)
    """
    dx = vertex[0] - center[0]
    dy = vertex[1] - center[1]

    # atan2 gives angle from +X axis, counterclockwise
    # We need angle from +Y axis (North), clockwise
    angle = math.atan2(dx, -dy)  # Negate dy for Y-down coords

    # Ensure positive angle
    if angle < 0:
        angle += 2 * math.pi

    return angle


def angle_distance(a1: float, a2: float) -> float:
    """Calculate shortest angular distance between two angles

    Args:
        a1, a2: Angles in radians

    Returns:
        Shortest distance in radians (always positive)
    """
    diff = (a2 - a1) % (2 * math.pi)
    if diff > math.pi:
        diff = 2 * math.pi - diff
    return diff


def rotate_vertices(
    vertices: List[Tuple[float, float]], rotation_degrees: float
) -> List[Tuple[float, float]]:
    """Rotate vertices by given angle

    Args:
        vertices: List of (x, y) tuples
        rotation_degrees: Rotation in degrees (Vood system: 0° = North, clockwise)

    Returns:
        Rotated vertices
    """
    if rotation_degrees == 0:
        return vertices

    # Convert to radians
    angle_rad = math.radians(rotation_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    rotated = []
    for x, y in vertices:
        # Standard rotation matrix
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        rotated.append((rx, ry))

    return rotated
