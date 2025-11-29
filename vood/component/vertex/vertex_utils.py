"""Utility functions for vertex operations"""

from __future__ import annotations
import math
from statistics import mean
from vood.core.point2d import Points2D, Point2D


def centroid(vertices: Points2D) -> Point2D:
    """Calculate the centroid (center of mass) of a set of vertices

    Args:
        vertices: List of Point2D objects

    Returns:
        Point2D centroid position
    """
    if not vertices:
        return Point2D(0.0, 0.0)

    xs, ys = zip(*vertices)
    return Point2D(mean(xs), mean(ys))


def angle_from_centroid(vertex: Point2D, center: Point2D) -> float:
    """Calculate angle of vertex from centroid in Vood coordinates

    Vood uses: 0° = North (up), 90° = East (right), clockwise

    Args:
        vertex: (x, y) position
        center: (cx, cy) centroid position

    Returns:
        Angle in radians (0 to 2π)
    """
    dx = vertex.x - center.x
    dy = vertex.y - center.y

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


def rotate_vertices(vertices: Points2D, rotation_degrees: float) -> Points2D:
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
        rotated.append(Point2D(rx, ry))

    return rotated


def rotate_vertices_inplace(vertices: Points2D, rotation_degrees: float) -> None:
    """Rotate vertices in-place by given angle

    Mutates the input vertex list directly. More efficient than rotate_vertices()
    for temporary transformations during alignment.

    Args:
        vertices: List of Point2D objects to rotate in-place
        rotation_degrees: Rotation in degrees (Vood system: 0° = North, clockwise)
    """
    if rotation_degrees == 0:
        return

    # Convert to radians
    angle_rad = math.radians(rotation_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    for v in vertices:
        # Store original x for calculation
        x_orig = v.x
        # Apply rotation matrix in-place
        v.x = x_orig * cos_a - v.y * sin_a
        v.y = x_orig * sin_a + v.y * cos_a


def rotate_list_inplace(lst: list, offset: int) -> None:
    """Rotate a list in-place by offset positions

    Uses the reversal algorithm for O(n) time with O(1) space.
    More efficient than slicing (lst[offset:] + lst[:offset]).

    Args:
        lst: List to rotate in-place
        offset: Number of positions to rotate (positive = left rotation)

    Example:
        lst = [1, 2, 3, 4, 5]
        rotate_list_inplace(lst, 2)
        # lst is now [3, 4, 5, 1, 2]
    """
    if not lst or offset == 0:
        return

    n = len(lst)
    offset = offset % n  # Handle offset > n

    if offset == 0:
        return

    # Reversal algorithm: reverse three times
    # [1,2,3,4,5] with offset=2 -> [3,4,5,1,2]
    # Step 1: Reverse first offset elements: [2,1,3,4,5]
    # Step 2: Reverse remaining elements: [2,1,5,4,3]
    # Step 3: Reverse entire list: [3,4,5,1,2]

    def reverse_range(start: int, end: int) -> None:
        """Reverse elements in range [start, end)"""
        i, j = start, end - 1
        while i < j:
            lst[i], lst[j] = lst[j], lst[i]
            i += 1
            j -= 1

    reverse_range(0, offset)
    reverse_range(offset, n)
    reverse_range(0, n)
