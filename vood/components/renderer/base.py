"""Abstract base classes for renderers and states in the vood framework"""

from __future__ import annotations
from abc import ABC, abstractmethod

import drawsvg as dw
from vood.components.states import State


class Renderer(ABC):
    """Abstract base class for all renderer classes

    Each renderer must implement core geometry in _render_core.
    The base render method applies transforms and opacity.
    """

    @abstractmethod
    def _render_core(self, state: State) -> dw.DrawingElement:
        """Render the shape itself (without transforms)
        Subclasses must implement this method.
        """
        pass

    def render(self, state: State) -> dw.DrawingElement:
        elem = self._render_core(state)
        transforms = []
        # SVG applies transforms right-to-left, so order is: translate, rotate, scale
        if state.x != 0 or state.y != 0:
            transforms.append(f"translate({state.x},{state.y})")
        if state.rotation != 0:
            transforms.append(f"rotate({state.rotation})")
        if state.scale != 1.0:
            transforms.append(f"scale({state.scale})")
        group = dw.Group()
        group.append(elem)
        group.args["opacity"] = state.opacity
        if transforms:
            group.args["transform"] = " ".join(transforms)

        return group
