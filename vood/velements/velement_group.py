"""Element transform group for hierarchical animation with advanced transforms"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable, Dict, Any

import drawsvg as dw

from vood.components import State
from vood.velements.base_velement import BaseVElement
from vood.transitions import easing

# Forward reference to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .velement import VElement


@dataclass(frozen=True)
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
        **State.DEFAULT_EASING,
        "transform_origin_x": easing.in_out,
        "transform_origin_y": easing.in_out,
        "scale_x": easing.in_out,
        "scale_y": easing.in_out,
        "skew_x": easing.in_out,
        "skew_y": easing.in_out,
    }


class VElementGroup(BaseVElement):
    """Element transform group with complete SVG transform capabilities

    Supports advanced transforms including custom transform origins, non-uniform scaling,
    skew transforms, and global transitions. Can hold and animate other elements
    with full transform control.

    Features:
    - All BaseVElement animation capabilities (keyframes, states, global_transitions)
    - Complete SVG transform support (translate, rotate, scale, skew)
    - Per-segment and global easing control
    - Hierarchical animation (animates children at synchronized time)
    - Child elements that don't exist at current time are automatically skipped
    """

    def __init__(
        self,
        *,
        elements: Optional[List[VElement]] = None,
        state: Optional[VElementGroupState] = None,
        states: Optional[List[VElementGroupState]] = None,
        keyframes: Optional[List[Tuple[float, VElementGroupState]]] = None,
        global_transitions: Optional[Dict[str, Tuple[Any, Any]]] = None,
        easing: Optional[Dict[str, Callable[[float], float]]] = None,
        segment_easing: Optional[Dict[int, Dict[str, Callable[[float], float]]]] = None,
    ) -> None:
        """Initialize an element group with full animation capabilities

        Args:
            elements: List of child elements to group
            state: Single state for static group
            states: List of states for evenly-timed animation
            keyframes: List of (frame_time, state) tuples for precise timing
            global_transitions: Dict of property_name -> (start_value, end_value)
                for properties that should transition linearly across entire animation
                independent of keyframe structure. Useful for properties like opacity
                that should fade smoothly across the entire timeline.
            easing: Optional dict to override default easing functions for all segments.
                Example: {"scale": easing.bounce, "rotation": easing.elastic}
            segment_easing: Optional dict of segment_index -> {property: easing_func}
                to override easing for specific segments. Segment 0 is between keyframe[0]
                and keyframe[1], etc.
                Example: {0: {"scale": easing.bounce}, 1: {"rotation": easing           .elastic}}

        Examples:
            # Static group
            group = VElementGroup(
                elements=[elem1, elem2],
                state=VElementGroupState(x=100, y=100, scale=2.0)
            )

            # Animated with keyframes and global opacity fade
            group = VElementGroup(
                elements=[elem1, elem2],
                keyframes=[
                    (0.0, VElementGroupState(x=0, rotation=0)),
                    (0.5, VElementGroupState(x=100, rotation=180)),
                    (1.0, VElementGroupState(x=200, rotation=360))
                ],
                global_transitions={"opacity": (1.0, 0.0)},  # Fade out during animation
                easing={"rotation": easing.elastic}
            )

            # Advanced: Per-segment easing control
            group = VElementGroup(
                elements=[elem1, elem2],
                keyframes=[
                    (0.0, VElementGroupState(x=0, scale=1.0)),
                    (0.5, VElementGroupState(x=100, scale=2.0)),
                    (1.0, VElementGroupState(x=200, scale=1.0))
                ],
                segment_easing={
                    0: {"scale": easing.bounce},  # Bounce in first half
                    1: {"scale": easing.elastic}  # Elastic in second half
                }
            )
        """
        # Initialize the base animation system with ALL parameters
        super().__init__(
            state=state,
            states=states,
            keyframes=keyframes,
            global_transitions=global_transitions,
            easing=easing,
            segment_easing=segment_easing,
        )

        # Store the elements
        self.elements = elements if elements else []

    def render(self) -> Optional[dw.Group]:
        """Render the element group in its initial state (static rendering)

        Returns:
            drawsvg Group element representing the group and its elements
            or None if group doesn't exist at t=0.0
        """
        return self.render_at_frame_time(0.0)

    def render_at_frame_time(self, t: float) -> Optional[dw.Group]:
        """Render the element transform group at a specific animation time

        Args:
            t: Time factor from 0.0 to 1.0

        Returns:
            drawsvg Group element representing the group at time t
            if group doesn't exist at this time (outside keyframe range)
        """
        # Get group's state at time t (using inherited method)
        # This automatically handles keyframe interpolation, easing, and global_transitions
        group_state = self._get_state_at_time(t)
        # If no state (outside keyframe range), don't render the group
        if group_state is None:
            return None
        # Build transform string
        transform_string = self._build_transform_string(group_state)

        # Create group for the container
        if transform_string:
            group = dw.Group(transform=transform_string)
        else:
            group = dw.Group()

        # Render each child and add to group
        for child in self.elements:
            child_element = None
            if hasattr(child, "render_at_frame_time") and child.is_animatable():
                # Child is animatable - render at current time
                child_element = child.render_at_frame_time(t)
            else:
                # Child is static - render normally
                child_element = child.render()

            if child_element is not None:
                group.append(child_element)

        # Apply opacity to the group
        if group_state.opacity != 1.0:
            group.opacity = group_state.opacity

        return group

    def _build_transform_string(self, state: VElementGroupState) -> str:
        """Build SVG transform string from state with advanced transform support

        The transform order follows SVG best practices:
        1. Translate to transform origin (if needed)
        2. Apply position translation
        3. Apply rotation
        4. Apply scaling (uniform or non-uniform)
        5. Apply skew transforms
        6. Translate back from transform origin (if needed)

        Args:
            state: Transform group state containing all transform properties

        Returns:
            SVG transform string or empty string if no transforms needed
        """
        transform_parts = []

        # Check which transforms are active
        has_transform_origin = (
            state.transform_origin_x != 0 or state.transform_origin_y != 0
        )
        has_rotation = state.rotation != 0
        has_non_uniform_scale = (
            state.scale_x != 1.0 or state.scale_y != 1.0
        ) or state.scale != 1.0
        has_skew = state.skew_x != 0 or state.skew_y != 0

        # Step 1: Translate to transform origin if needed
        if has_transform_origin and (has_rotation or has_non_uniform_scale or has_skew):
            transform_parts.append(
                f"translate({state.transform_origin_x}, {state.transform_origin_y})"
            )

        # Step 2: Apply position translation
        if state.x != 0 or state.y != 0:
            transform_parts.append(f"translate({state.x}, {state.y})")

        # Step 3: Apply rotation
        if state.rotation != 0:
            transform_parts.append(f"rotate({state.rotation})")

        # Step 4: Apply scaling
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

        # Step 5: Apply skew transforms
        if state.skew_x != 0:
            transform_parts.append(f"skewX({state.skew_x})")

        if state.skew_y != 0:
            transform_parts.append(f"skewY({state.skew_y})")

        # Step 6: Translate back from transform origin if needed
        if has_transform_origin and (has_rotation or has_non_uniform_scale or has_skew):
            transform_parts.append(
                f"translate({-state.transform_origin_x}, {-state.transform_origin_y})"
            )

        return " ".join(transform_parts)

    def get_elements(self) -> List[VElement]:
        """Get the list of child elements

        Returns:
            List of child elements (copy to prevent external modification)
        """
        return self.elements.copy()

    def add_element(self, child: VElement) -> None:
        """Add a child element to the group

        Args:
            child: Element to add
        """
        self.elements.append(child)

    def add_elements(self, elements: List[VElement]) -> None:
        """Add multiple child elements to the group

        Args:
            elements: List of elements to add
        """
        self.elements.extend(elements)

    def remove_element(self, child: VElement) -> None:
        """Remove a child element from the group

        Args:
            child: Element to remove

        Raises:
            ValueError: If child is not in the group
        """
        if child in self.elements:
            self.elements.remove(child)
        else:
            raise ValueError("Element not found in group")

    def clear_elements(self) -> None:
        """Remove all child elements from the group"""
        self.elements.clear()

    def is_empty(self) -> bool:
        """Check if the group has no child elements

        Returns:
            True if group is empty, False otherwise
        """
        return len(self.elements) == 0
