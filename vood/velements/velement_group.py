"""Element transform group for hierarchical animation with advanced transforms"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable, Dict

import drawsvg as dw

from vood.components.base import State
from vood.velements.base_velement import BaseVElement
from vood.transitions.easing import Easing

# Forward reference to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .velement import VElement


@dataclass
class VElementGroupState(State):
    """State class for element transform groups with complete SVG transform capabilities

    Inherits basic transform properties from base State and adds advanced transforms:
    - Custom transform origins for rotation/scaling center points
    - Non-uniform scaling (separate X/Y scaling factors)
    - Skew transforms for perspective effects
    """

    # Advanced transform properties
    transform_origin_x: float = 0  # Transform center point X
    transform_origin_y: float = 0  # Transform center point Y
    scale_x: float = 1.0  # Non-uniform scaling X
    scale_y: float = 1.0  # Non-uniform scaling Y
    skew_x: float = 0  # Skew transform X (degrees)
    skew_y: float = 0  # Skew transform Y (degrees)

    DEFAULT_EASING = {
        "x": Easing.in_out,
        "y": Easing.in_out,
        "scale": Easing.in_out,
        "rotation": Easing.in_out,
        "opacity": Easing.linear,
        "transform_origin_x": Easing.in_out,
        "transform_origin_y": Easing.in_out,
        "scale_x": Easing.in_out,
        "scale_y": Easing.in_out,
        "skew_x": Easing.in_out,
        "skew_y": Easing.in_out,
    }


class VElementGroup(BaseVElement):
    """Element transform group with complete SVG transform capabilities

    Supports advanced transforms including custom transform origins, non-uniform scaling,
    skew transforms, and direct matrix transforms. Can hold and animate other elements
    with full transform control.
    """

    def __init__(
        self,
        *,
        elements: List[VElement] = None,
        state: Optional[VElementGroupState] = None,
        states: Optional[List[VElementGroupState]] = None,
        keyframes: Optional[List[Tuple[float, VElementGroupState]]] = None,
        easing: Optional[Dict[str, Callable[[float], float]]] = None,
    ) -> None:
        """Initialize an element group, which handles
            * positioning
            * scaling
            * rotation
            * opacity
            of the grouped child elements.

        Args:
            elements: List of child elements to group
            state: Single state for static group
            states: List of states for evenly-timed animation
            keyframes: List of (frame_time, state) tuples for precise timing
            easing: Optional dict to override default easing functions
        """
        # Initialize the base animation system
        super().__init__(state=state, states=states, keyframes=keyframes, easing=easing)

        # Store the elements
        self.elements = elements if elements else []

    def render(self) -> dw.Group:
        """Render the element group in its initial state (static rendering)

        Returns:
            drawsvg Group element representing the group and its elements
        """
        return self.render_at_frame_time(0.0)

    def render_at_frame_time(self, t: float) -> dw.Group:
        """Render the element transform group at a specific animation time

        Args:
            t: Time factor from 0.0 to 1.0

        Returns:
            drawsvg Group element representing the group at time t
        """
        # Get group's state at time t (using inherited method)
        group_state = self._get_state_at_time(t)

        # Build transform string
        transform_string = self._build_transform_string(group_state)

        # Create group for the container
        if transform_string:
            group = dw.Group(transform=transform_string)
        else:
            group = dw.Group()

        # Render each child and add to group
        for child in self.elements:
            if hasattr(child, "render_at_frame_time") and child.is_animatable():
                # Child is animatable - render at current time
                child_element = child.render_at_frame_time(t)
            else:
                # Child is static - render normally
                child_element = child.render()

            group.append(child_element)

        # Apply opacity to the group
        if group_state.opacity != 1.0:
            group.opacity = group_state.opacity

        return group

    def _build_transform_string(self, state: VElementGroupState) -> str:
        """Build SVG transform string from state with advanced transform support

        Args:
            state: Transform group state containing all transform properties

        Returns:
            SVG transform string or empty string if no transforms needed
        """
        transform_parts = []

        # Step 1: Translate to transform origin if needed
        has_transform_origin = (
            state.transform_origin_x != 0 or state.transform_origin_y != 0
        )
        has_rotation = state.rotation != 0
        has_non_uniform_scale = (
            state.scale_x != 1.0 or state.scale_y != 1.0
        ) or state.scale != 1.0
        has_skew = state.skew_x != 0 or state.skew_y != 0

        if has_transform_origin and (has_rotation or has_non_uniform_scale or has_skew):
            transform_parts.append(
                f"translate({state.transform_origin_x}, {state.transform_origin_y})"
            )

        # Step 2: Apply transforms in order: translate -> rotate -> scale -> skew
        if state.x != 0 or state.y != 0:
            transform_parts.append(f"translate({state.x}, {state.y})")

        if state.rotation != 0:
            transform_parts.append(f"rotate({state.rotation})")

        # Handle both uniform and non-uniform scaling
        if state.scale != 1.0 and (state.scale_x == 1.0 and state.scale_y == 1.0):
            # Use uniform scale if non-uniform scales are at default
            transform_parts.append(f"scale({state.scale})")
        elif state.scale_x != 1.0 or state.scale_y != 1.0:
            # Use non-uniform scaling (and apply uniform scale multiplier if present)
            final_scale_x = state.scale_x * state.scale
            final_scale_y = state.scale_y * state.scale
            transform_parts.append(f"scale({final_scale_x}, {final_scale_y})")
        elif state.scale != 1.0:
            # Only uniform scale is set
            transform_parts.append(f"scale({state.scale})")

        if state.skew_x != 0:
            transform_parts.append(f"skewX({state.skew_x})")

        if state.skew_y != 0:
            transform_parts.append(f"skewY({state.skew_y})")

        # Step 3: Translate back from transform origin if needed
        if has_transform_origin and (has_rotation or has_non_uniform_scale or has_skew):
            transform_parts.append(
                f"translate({-state.transform_origin_x}, {-state.transform_origin_y})"
            )

        return " ".join(transform_parts)

    def get_elements(self) -> List[VElement]:
        """Get the list of child elements

        Returns:
            List of child elements
        """
        return self.elements.copy()

    def add_element(self, child: VElement) -> None:
        """Add a child element to the container

        Args:
            child: Element to add
        """
        self.elements.append(child)

    def add_elements(self, elements: List[VElement]) -> None:
        """Add multiple child elements to the container

        Args:
            elements: List of elements to add
        """
        self.elements.extend(elements)

    def remove_element(self, child: VElement) -> None:
        """Remove a child element from the container

        Args:
            child: Element to remove
        """
        if child in self.elements:
            self.elements.remove(child)
