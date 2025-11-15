"""
Morph system for geometric primitives with vertex-based morphing.

This implements a Manim-inspired approach where shapes are represented as
point clouds that can be smoothly morphed into each other.

Key features:
- All shapes have the same number of vertices (num_points)
- Vertices are generated procedurally from shape parameters
- Open shapes (lines) can morph into closed shapes (circles) with fill fade-in
- Smart vertex alignment for smooth morphing
"""

from __future__ import annotations
import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional

import drawsvg as dw

from vood.components.states.base import State
from vood.components.renderer.base import Renderer
from vood.transitions import easing
from vood.core.color import Color


# ============================================================================
# Base State
# ============================================================================

@dataclass(frozen=True)
class MorphState(State):
    """Base state for vertex-based morphable shapes
    
    All morph shapes share:
    - num_points: Resolution (number of vertices)
    - closed: Whether the shape is closed (affects fill)
    
    Subclasses override get_vertices() to generate their specific geometry.
    Subclasses should define their own color properties as needed.
    """
    
    num_points: int = 64  # Vertex resolution - must match for morphing!
    closed: bool = True  # Whether shape is closed
    
    # Default easing
    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "num_points": easing.step,  # Can't smoothly change resolution
        "closed": easing.step,  # Boolean
    }
    
    @abstractmethod
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Generate vertices for this shape
        
        Must return exactly num_points vertices.
        Vertices should be centered at origin (0, 0).
        """
        raise NotImplementedError


# ============================================================================
# Concrete Shape States
# ============================================================================

@dataclass(frozen=True)
class MorphCircleState(MorphState):
    """Circle with evenly distributed vertices"""
    
    radius: float = 50
    fill_color: Optional[Color] = (100, 150, 255)
    stroke_color: Optional[Color] = None
    stroke_width: float = 2
    
    DEFAULT_EASING = {
        **MorphState.DEFAULT_EASING,
        "radius": easing.in_out,
        "fill_color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }
    
    def __post_init__(self):
        super().__post_init__()
        self._normalize_color_field("fill_color")
        self._normalize_color_field("stroke_color")
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Generate circle vertices, starting at 0° (North/top) going clockwise"""
        return [
            (
                self.radius * math.sin(2 * math.pi * i / self.num_points),
                -self.radius * math.cos(2 * math.pi * i / self.num_points)
            )
            for i in range(self.num_points)
        ]


@dataclass(frozen=True)
class MorphTriangleState(MorphState):
    """Equilateral triangle with vertices distributed along perimeter"""
    
    size: float = 50  # Distance from center to vertex
    fill_color: Optional[Color] = (100, 150, 255)
    stroke_color: Optional[Color] = None
    stroke_width: float = 2
    
    DEFAULT_EASING = {
        **MorphState.DEFAULT_EASING,
        "size": easing.in_out,
        "fill_color": easing.linear,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }
    
    def __post_init__(self):
        super().__post_init__()
        self._normalize_color_field("fill_color")
        self._normalize_color_field("stroke_color")
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Generate triangle vertices distributed along perimeter
        
        Triangle points upward with vertices at:
        - Top: 0° (North/straight up)
        - Bottom-right: 120° 
        - Bottom-left: 240°
        """
        # Calculate triangle vertices (pointing up, Vood coordinate system)
        triangle_verts = []
        for i in range(3):
            angle = math.radians(i * 120)  # 0°, 120°, 240°
            triangle_verts.append((
                self.size * math.sin(angle),
                -self.size * math.cos(angle)
            ))
        
        # Calculate perimeter lengths between vertices
        def distance(p1, p2):
            return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        edge_lengths = [
            distance(triangle_verts[i], triangle_verts[(i + 1) % 3])
            for i in range(3)
        ]
        total_perimeter = sum(edge_lengths)
        
        # Distribute num_points along the perimeter
        vertices = []
        current_edge = 0
        distance_along_edge = 0
        
        for i in range(self.num_points):
            # Target distance along total perimeter
            target_distance = (i / self.num_points) * total_perimeter
            
            # Find which edge we're on
            cumulative = 0
            for edge_idx in range(3):
                if cumulative + edge_lengths[edge_idx] >= target_distance:
                    current_edge = edge_idx
                    distance_along_edge = target_distance - cumulative
                    break
                cumulative += edge_lengths[edge_idx]
            
            # Interpolate along current edge
            v1 = triangle_verts[current_edge]
            v2 = triangle_verts[(current_edge + 1) % 3]
            t = distance_along_edge / edge_lengths[current_edge]
            
            x = v1[0] + t * (v2[0] - v1[0])
            y = v1[1] + t * (v2[1] - v1[1])
            vertices.append((x, y))
        
        return vertices


@dataclass(frozen=True)
class MorphLineState(MorphState):
    """Straight line with vertices distributed along its length
    
    Note: Lines are open shapes (closed=False by default).
    When morphing into closed shapes, the endpoints will be connected
    for fill area determination.
    """
    
    length: float = 100
    closed: bool = False  # Lines are open by default
    stroke_color: Optional[Color] = (0, 0, 0)
    stroke_width: float = 2
    
    DEFAULT_EASING = {
        **MorphState.DEFAULT_EASING,
        "length": easing.in_out,
        "stroke_color": easing.linear,
        "stroke_width": easing.in_out,
    }
    
    def __post_init__(self):
        super().__post_init__()
        self._normalize_color_field("stroke_color")
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Generate line vertices from -length/2 to +length/2 along x-axis"""
        half_length = self.length / 2
        return [
            (
                -half_length + (i / (self.num_points - 1)) * self.length,
                0
            )
            for i in range(self.num_points)
        ]


# ============================================================================
# Renderer
# ============================================================================

class MorphRenderer(Renderer):
    """Renderer for morphable geometric shapes
    
    Handles both open and closed shapes, with special logic for fill behavior:
    - Open shapes (lines): No fill, only stroke
    - Closed shapes: Both fill and stroke
    - During morphing: Fill fades in/out smoothly
    
    The key Manim-inspired feature: when morphing from open to closed,
    we implicitly connect the endpoints for fill determination without
    drawing that connecting line.
    """
    
    def _render_core(self, state: MorphState) -> dw.Group:
        """Render the morphable shape
        
        Args:
            state: MorphState containing shape parameters
            
        Returns:
            drawsvg Group containing the rendered shape
        """
        vertices = state.get_vertices()
        
        # Flatten vertices for drawsvg
        coords = [coord for x, y in vertices for coord in (x, y)]
        
        group = dw.Group()
        
        # Build rendering kwargs
        lines_kwargs = {}
        
        # Fill handling (Manim-style)
        if state.closed and state.fill_color:
            # Closed shape with fill color
            lines_kwargs["fill"] = state.fill_color.to_rgb_string()
            lines_kwargs["close"] = True
        elif not state.closed and state.fill_color and state.fill_color.a > 0:
            # Open shape morphing into closed: show fill but don't close stroke
            # This creates the "ghost connection" for fill area
            lines_kwargs["fill"] = state.fill_color.to_rgb_string()
            lines_kwargs["close"] = True  # Close for fill only
            
            # We'll draw stroke separately without closing
        else:
            # No fill
            lines_kwargs["fill"] = "none"
            lines_kwargs["close"] = state.closed
        
        # Stroke handling
        if state.stroke_color and state.stroke_width > 0:
            stroke_color = state.stroke_color.to_rgb_string()
            
            if not state.closed and state.fill_color and state.fill_color.a > 0:
                # Special case: open shape with fill
                # Draw fill area first (closed)
                fill_lines = dw.Lines(
                    *coords,
                    fill=state.fill_color.to_rgb_string(),
                    stroke="none",
                    close=True
                )
                group.append(fill_lines)
                
                # Then draw stroke without closing
                stroke_lines = dw.Lines(
                    *coords,
                    fill="none",
                    stroke=stroke_color,
                    stroke_width=state.stroke_width,
                    close=False  # Don't close the stroke!
                )
                group.append(stroke_lines)
                return group
            else:
                # Normal stroke
                lines_kwargs["stroke"] = stroke_color
                lines_kwargs["stroke_width"] = state.stroke_width
        
        # Create the shape
        lines = dw.Lines(*coords, **lines_kwargs)
        group.append(lines)
        
        return group


# ============================================================================
# Usage Example (for documentation)
# ============================================================================

"""
Example usage:

from vood.core import VElement, Animation

# Create a circle
circle = VElement(
    MorphRenderer(),
    state=MorphCircleState(
        radius=50,
        num_points=64,
        fill_color=(100, 150, 255),
        stroke_color=(0, 0, 0),
        stroke_width=2
    )
)

# Create a triangle
triangle = VElement(
    MorphRenderer(),
    state=MorphTriangleState(
        size=50,
        num_points=64,
        fill_color=(255, 100, 100),
        stroke_color=(0, 0, 0),
        stroke_width=2
    )
)

# Create a line
line = VElement(
    MorphRenderer(),
    state=MorphLineState(
        length=100,
        num_points=64,
        closed=False,  # Lines are open
        stroke_color=(0, 0, 0),
        stroke_width=2
    )
)

# Morph circle into triangle (next step: implement interpolation)
animation = Animation(
    element=circle,
    keystates=[
        (0.0, MorphCircleState(radius=50, num_points=64)),
        (1.0, MorphTriangleState(size=50, num_points=64))
    ],
    duration=2.0
)

# Morph line into circle (fill will fade in smoothly)
animation = Animation(
    element=line,
    keystates=[
        (0.0, MorphLineState(length=100, num_points=64, closed=False)),
        (1.0, MorphCircleState(radius=50, num_points=64, closed=True, 
                              fill_color=(100, 150, 255)))
    ],
    duration=2.0
)
"""