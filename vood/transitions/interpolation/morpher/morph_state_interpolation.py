"""
Morphing interpolation system for MorphState shapes.

This implements the intelligent vertex alignment and interpolation
needed to smoothly morph between different geometric shapes.

Key features:
- Automatic vertex alignment based on angular position
- Smart handling of open/closed shape transitions
- Fill color fade-in/out during open↔closed morphing
- Support for morphing between different shape types
"""

from __future__ import annotations
import math
from dataclasses import dataclass, replace
from typing import List, Tuple, Optional, Any

from vood.core.color import Color


# ============================================================================
# Vertex Alignment Algorithm
# ============================================================================


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

    # Convert to Vood coordinate system
    # Standard atan2 gives: 0° = East, counter-clockwise
    # We want: 0° = North, clockwise
    angle = math.atan2(dx, -dy)  # Swap and negate for North = 0

    # Normalize to 0-2π range
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


def align_vertices(
    verts1: List[Tuple[float, float]],
    verts2: List[Tuple[float, float]],
    rotation1: float = 0,
    rotation2: float = 0,
) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    """Align two vertex lists for optimal morphing

    Uses angular alignment based on vertex positions relative to centroids.
    Rotates the second vertex list to minimize total angular distance.
    Takes into account the rotation state of both shapes.

    Args:
        verts1: First vertex list
        verts2: Second vertex list (must have same length as verts1)
        rotation1: Rotation of first shape in degrees
        rotation2: Rotation of second shape in degrees

    Returns:
        Tuple of (verts1, verts2_aligned) where verts2 is rotated for best match
    """
    if len(verts1) != len(verts2):
        raise ValueError(
            f"Vertex lists must have same length: {len(verts1)} != {len(verts2)}"
        )

    if not verts1 or not verts2:
        return verts1, verts2

    # Apply shape rotations to vertices for alignment calculation
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

    # Rotate verts2 (ORIGINAL, not rotated) by best_offset
    # We align the original vertices, not the rotated ones
    verts2_aligned = verts2[best_offset:] + verts2[:best_offset]

    return verts1, verts2_aligned


# ============================================================================
# Interpolation Helpers
# ============================================================================


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values"""
    return a + (b - a) * t


def lerp_vertices(
    verts1: List[Tuple[float, float]], verts2: List[Tuple[float, float]], t: float
) -> List[Tuple[float, float]]:
    """Interpolate between two vertex lists

    Args:
        verts1: Starting vertices
        verts2: Ending vertices
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated vertex list
    """
    if len(verts1) != len(verts2):
        raise ValueError("Vertex lists must have same length for interpolation")

    return [
        (lerp(v1[0], v2[0], t), lerp(v1[1], v2[1], t)) for v1, v2 in zip(verts1, verts2)
    ]


# ============================================================================
# Raw Morph State (holds interpolated vertices)
# ============================================================================


@dataclass(frozen=True)
class MorphRawState:
    """Raw morph state holding interpolated vertices

    This is used internally during morphing to hold the result
    of vertex interpolation. It's not meant to be created by users.
    """

    # Common State properties
    x: float = 0
    y: float = 0
    scale: float = 1.0
    opacity: float = 1.0
    rotation: float = 0

    # Morph properties
    num_points: int = 64
    closed: bool = True
    vertices: List[Tuple[float, float]] = None

    # Colors
    fill_color: Optional[Color] = None
    stroke_color: Optional[Color] = None
    stroke_width: float = 2

    def get_vertices(self) -> List[Tuple[float, float]]:
        """Return the pre-computed vertices"""
        return self.vertices if self.vertices else []


# ============================================================================
# Morph Interpolation Function
# ============================================================================


def interpolate_morph_states(state1: Any, state2: Any, t: float) -> MorphRawState:
    """Interpolate between two MorphState instances

    This is the main morphing function that handles:
    - Vertex alignment and interpolation (accounting for rotation)
    - Color interpolation (including fill fade-in/out)
    - Open/closed transition handling
    - All common state properties

    Args:
        state1: Starting MorphState
        state2: Ending MorphState
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        MorphRawState with interpolated properties
    """

    # Verify both states have same num_points
    if state1.num_points != state2.num_points:
        raise ValueError(
            f"Cannot morph shapes with different num_points: "
            f"{state1.num_points} != {state2.num_points}. "
            f"Both shapes must have the same vertex resolution."
        )

    # Get vertices from both states (these are un-rotated, centered at origin)
    verts1 = state1.get_vertices()
    verts2 = state2.get_vertices()

    # Align vertices for optimal morphing, taking rotation into account
    verts1_aligned, verts2_aligned = align_vertices(
        verts1, verts2, rotation1=state1.rotation, rotation2=state2.rotation
    )

    # Interpolate vertices
    interpolated_verts = lerp_vertices(verts1_aligned, verts2_aligned, t)

    # Interpolate closed flag (step function at t=0.5)
    closed = state2.closed if t >= 0.5 else state1.closed

    # Handle fill color interpolation
    # Special case: open → closed transition
    fill_color = None

    fill1 = getattr(state1, "fill_color", None)
    fill2 = getattr(state2, "fill_color", None)

    if fill1 and fill2:
        # Both have fill colors - normal interpolation
        fill_color = fill1.interpolate(fill2, t)
    elif not fill1 and fill2:
        # Open → closed: fade in fill color
        # Start with transparent version of target color
        fill_color = Color(fill2.r, fill2.g, fill2.b, 0).interpolate(fill2, t)
    elif fill1 and not fill2:
        # Closed → open: fade out fill color
        fill_color = fill1.interpolate(Color(fill1.r, fill1.g, fill1.b, 0), t)
    # else: both None, no fill

    # Handle stroke color interpolation
    stroke_color = None

    stroke1 = getattr(state1, "stroke_color", None)
    stroke2 = getattr(state2, "stroke_color", None)

    if stroke1 and stroke2:
        stroke_color = stroke1.interpolate(stroke2, t)
    elif not stroke1 and stroke2:
        # Fade in stroke
        stroke_color = Color(stroke2.r, stroke2.g, stroke2.b, 0).interpolate(stroke2, t)
    elif stroke1 and not stroke2:
        # Fade out stroke
        stroke_color = stroke1.interpolate(Color(stroke1.r, stroke1.g, stroke1.b, 0), t)

    # Interpolate stroke width
    width1 = getattr(state1, "stroke_width", 0)
    width2 = getattr(state2, "stroke_width", 0)
    stroke_width = lerp(width1, width2, t)

    # Interpolate common state properties
    x = lerp(state1.x, state2.x, t)
    y = lerp(state1.y, state2.y, t)
    scale = lerp(state1.scale, state2.scale, t)
    opacity = lerp(state1.opacity, state2.opacity, t)

    # Handle rotation (shortest path)
    rot_diff = (state2.rotation - state1.rotation) % 360
    if rot_diff > 180:
        rot_diff -= 360
    rotation = state1.rotation + rot_diff * t

    # Create and return raw state
    # Note: vertices are stored un-rotated; rotation is applied by renderer
    return MorphRawState(
        x=x,
        y=y,
        scale=scale,
        opacity=opacity,
        rotation=rotation,
        num_points=state1.num_points,
        closed=closed,
        vertices=interpolated_verts,
        fill_color=fill_color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )


# ============================================================================
# Integration with MorphState
# ============================================================================


def add_morph_interpolation_to_state():
    """
    This function should be called to add interpolation support to MorphState.

    In your actual vood codebase, you would add this method directly to the
    MorphState class:

    ```python
    class MorphState(State):
        # ... existing code ...

        def interpolate_with(self, other: 'MorphState', t: float) -> MorphRawState:
            return interpolate_morph_states(self, other, t)
    ```

    This allows the animation system to automatically use morphing when
    interpolating between two MorphState instances.
    """
    pass


# ============================================================================
# Usage Example
# ============================================================================

"""
Example usage in your animation system:

from vood.core import VElement, Animation
from vood.components.morph import (
    MorphRenderer, 
    MorphCircleState, 
    MorphTriangleState,
    MorphLineState
)

# Circle → Triangle morph
circle_to_triangle = VElement(
    MorphRenderer(),
    keystates=[
        (0.0, MorphCircleState(
            radius=50, 
            num_points=64,
            fill_color=(100, 150, 255),
            stroke_color=(0, 0, 0),
            stroke_width=2
        )),
        (1.0, MorphTriangleState(
            size=50, 
            num_points=64,
            fill_color=(255, 100, 100),
            stroke_color=(0, 0, 0),
            stroke_width=2
        ))
    ]
)

# Line → Circle morph (with fill fade-in!)
line_to_circle = VElement(
    MorphRenderer(),
    keystates=[
        (0.0, MorphLineState(
            length=100,
            num_points=64,
            closed=False,
            stroke_color=(0, 0, 0),
            stroke_width=2
        )),
        (1.0, MorphCircleState(
            radius=50,
            num_points=64,
            closed=True,
            fill_color=(100, 150, 255),
            stroke_color=(0, 0, 0),
            stroke_width=2
        ))
    ]
)

# The animation system will call interpolate_morph_states automatically!
"""
