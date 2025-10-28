"""Vood - SVG Animation Library

A Python library for creating beautiful SVG animations.
"""

# Main scene class
from .vscene.vscene import VScene

# Base elements
from .velements.velement import VElement
from .velements.velement_group import VElementGroup

# Components (shapes and elements)
from .components.circle import CircleState, CircleRenderer
from .components.rectangle import RectangleState, RectangleRenderer
from .components.ellipse import EllipseState, EllipseRenderer
from .components.triangle import TriangleState, TriangleRenderer
from .components.star import StarState, StarRenderer
from .components.line import LineState, LineRenderer
from .components.path import PathState, PathRenderer
from .components.text import TextState, TextRenderer
from .components.circle_text import CircleTextState, CircleTextRenderer
from .components.moon_phase import MoonPhaseState, MoonPhaseRenderer, MoonPhaseRenderer2
from .components.radial_segments import RadialSegmentsState, RadialSegmentsRenderer
from .components.double_circle import DoubleCircleState, DoubleCircleRenderer
from .components.raw_svg import RawSvgState, RawSvgRenderer
from .components.image import Image

# Transitions
from .transitions.easing import Easing
from .transitions.interpolation import Interpolation

# Optional: expose base classes if users might extend them
from .components.base import State, Renderer
from .velements.base_velement import BaseVElement

# Define public API
__all__ = [
    # Main
    "VScene",
    # Elements
    "VElement",
    "VElementGroup",
    # Components
    "CircleState",
    "CircleRenderer",
    "RectangleState",
    "RectangleRenderer",
    "EllipseState",
    "EllipseRenderer",
    "TriangleState",
    "TriangleRenderer",
    "StarState",
    "StarRenderer",
    "LineState",
    "LineRenderer",
    "PathState",
    "PathRenderer",
    "TextState",
    "TextRenderer",
    "CircleTextState",
    "CircleTextRenderer",
    "MoonPhaseState",
    "MoonPhaseRenderer",
    "MoonPhaseRenderer2",
    "RadialSegmentsState",
    "RadialSegmentsRenderer",
    "DoubleCircleState",
    "DoubleCircleRenderer",
    "RawSvgState",
    "RawSvgRenderer",
    "Image",
    # Transitions
    "Easing",
    "Interpolation",
    # Base classes
    "State",
    "Renderer",
]

__version__ = "0.1.0"
