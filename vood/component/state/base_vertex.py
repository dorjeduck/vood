"""Base state for vertex-based shapes with multi-contour support"""

from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

from vood.component.state.base import State
from vood.component.state.base_color import ColorState
from vood.component.vertex import VertexContours
from vood.transition import easing


@dataclass(frozen=True)
class VertexState(ColorState):
    """Base state for vertex-based morphable shapes with multi-contour support

    All vertex shapes share:
    - num_vertices: Resolution (number of vertices for outer contour)
    - closed: Whether the shape is closed (affects fill rendering)
    - fill_color: Fill color (works for both open and closed shapes, Manim-style)
    - stroke_color: Outline color
    - stroke_width: Outline width
    - _aligned_contours: Internal field for preprocessed alignment (don't set manually)

    For open shapes (lines), fill_color creates a "ghost" closing edge for fill area
    without drawing the closing line. This allows smooth fill fade-in during morphing.

    For shapes with  vertex_loops :
    - vertex loops are rendered using SVG masks (not evenodd fill-rule)
    - Hole strokes need 2x width since mask cuts through middle

    Subclasses override _generate_contours() to define their geometry.
    The get_contours() method automatically uses aligned contours if available.
    """

    closed: bool = True  # Whether shape is closed

    _num_vertices: Optional[int] = (
        None  # Vertex resolution (from config if not specified)
    )
    _aligned_contours: Optional[VertexContours] = None  # Internal use only

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "num_vertices": easing.step,
        "closed": easing.step,
        "_aligned_contours": easing.linear,  # Contours interpolate linearly
    }

    def __post_init__(self):
        super().__post_init__()

        # Apply config default for _num_vertices if not specified
        if self._num_vertices is None:
            from vood.config import get_config, ConfigKey

            config = get_config()
            num_verts = config.get(ConfigKey.STATE_VISUAL_NUM_VERTICES, 128)
            self._set_field("_num_vertices", num_verts)

    @abstractmethod
    def _generate_contours(self) -> VertexContours:
        """Generate contours for this shape (to be implemented by subclasses)

        Must return a VertexContours object with:
        - Outer contour with exactly num_vertices vertices
        - Optional hole contours

        Vertices should be centered at origin (0, 0).
        """
        raise NotImplementedError

    def get_vertex_renderer_class(self):
        """Get the renderer for morphing transitions (0 < t < 1)

        During morphing, we need vertex-based rendering to smoothly
        interpolate between different shapes.

        Returns:
            VertexRenderer class for morphing
        """
        from ..renderer.base_vertex import VertexRenderer

        return VertexRenderer

    def get_contours(self) -> VertexContours:
        """Get contours for this shape

        If alignment has been preprocessed, returns aligned contours.
        Otherwise, generates contours from shape parameters.
        """
        if self._aligned_contours is not None:
            return self._aligned_contours

        contours = self._generate_contours()

        # Validate vertex count matches _num_vertices
        actual_count = len(contours.outer.vertices)
        if actual_count != self._num_vertices:
            raise ValueError(
                f"{self.__class__.__name__} generated {actual_count} vertices "
                f"but _num_vertices is {self._num_vertices}. "
                f"Check the _generate_contours() implementation."
            )

        return contours

    # Backwards compatibility: keep get_vertices() for existing code
    def get_vertices(self):
        """Get outer contour vertices (backwards compatibility)

        Returns the vertices of the outer contour as a list of tuples.
        """
        contours = self.get_contours()
        return contours.outer.vertices
