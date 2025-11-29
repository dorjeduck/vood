"""Component system for vood - renderers and states for various shapes and elements"""

# Import submodules
from . import renderer
from . import state
from . import vertex

# Import registry functions
from .registry import (
    get_renderer_class_for_state,
    is_renderer_registered_for_state,
    get_all_registered_state_renderer_pairs,
    get_renderer_instance_for_state,
    clear_renderer_cache,
)

# Import all states
from .state import *

# Import all renderers
from .renderer import *

# Import vertex classes
from .vertex import *

# Import shape classes from perforated submodule
from .state.perforated import Shape, Circle, Ellipse, Rectangle, Polygon, Star, Astroid

__all__ = [
    # Submodules
    "renderer",
    "state",
    "vertex",
    # Registry functions
    "renderer",
    "get_renderer_class_for_state",
    "is_renderer_registered_for_state",
    "get_all_registered_state_renderer_pairs",
    "get_renderer_instance_for_state",
    "clear_renderer_cache",
    # Base classes
    "Renderer",
    "State",
    "VertexState",
    "VertexRenderer",
    # Vertex classes
    "Vertex",
    "VertexLoop",
    "VertexContours",
    "VertexEllipse",
    "VertexCircle",
    "VertexRectangle",
    "VertexLine",
    "VertexPolygon",
    # Shape classes
    "Shape",
    "Circle",
    "Ellipse",
    "Rectangle",
    "Polygon",
    "Star",
    "Astroid",
    # States (alphabetically sorted)
    "AstroidState",
    "CircleState",
    "CircleTextState",
    "DoubleCircleState",
    "EllipseState",
    "ImageState",
    "LineState",
    "MoonPhaseState",
    "PathState",
    "PathTextState",
    "PerforatedVertexState",
    "PerforatedCircleState",
    "PerforatedStarState",
    "PerforatedEllipseState",
    "PerforatedRectangleState",
    "PerforatedPolygonState",
    "PerforatedTriangleState",
    "PathAndTextVariantsState",
    "PathVariantsState",
    "PolyRingState",
    "RadialSegmentsState",
    "RawSvgState",
    "RectangleState",
    "RingState",
    "SquareRingState",
    "StarState",
    "TextState",
    "TriangleState",
    # Renderers (alphabetically sorted)
    "AstroidRenderer",
    "CircleRenderer",
    "CircleTextRenderer",
    "DoubleCircleRenderer",
    "EllipseRenderer",
    "ImageRenderer",
    "LineRenderer",
    "MoonPhaseRenderer",
    "PathRenderer",
    "PathTextRenderer",
    "PerforatedPrimitiveRenderer",
    "PathAndTextVariantsRenderer",
    "PathVariantsRenderer",
    "PolyRingRenderer",
    "RadialSegmentsRenderer",
    "RawSvgRenderer",
    "RectangleRenderer",
    "RingRenderer",
    "SquareRingRenderer",
    "StarRenderer",
    "TextRenderer",
    "TriangleRenderer",
]
