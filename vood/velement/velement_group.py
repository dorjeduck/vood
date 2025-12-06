from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable, Dict, Any

import drawsvg as dw

from vood.component import State

# Import the updated BaseVElement and its new types
from vood.velement.base_velement import BaseVElement
from vood.velement.keystate_parser import (
    FlexibleKeystateInput,
    PropertyKeyStatesConfig,
)
from vood.transition import easing

# Forward reference to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .velement import VElement


@dataclass(frozen=True)
class VElementGroupState(State):
    """State class for element transform groups with complete SVG transform capabilities"""

    transform_origin_x: float = 0
    transform_origin_y: float = 0
    scale_x: float = 1.0
    scale_y: float = 1.0
    skew_x: float = 0
    skew_y: float = 0

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
    """Element transform group with complete SVG transform capabilities"""

    def __init__(
        self,
        *,
        elements: Optional[List[VElement]] = None,
        state: Optional[VElementGroupState] = None,
        # Flexible keystates: accepts tuples, bare states, or KeyState objects
        keystates: Optional[List[FlexibleKeystateInput]] = None,
        # NEW/Renamed parameter replacing the old 'easing'
        property_easing: Optional[Dict[str, Callable[[float], float]]] = None,
        # NEW: Property Timelines (replaces global_transitions)
        property_keystates: Optional[PropertyKeyStatesConfig] = None,
        # REMOVED from signature: global_transitions, easing, segment_easing
    ) -> None:
        """Initialize an element group with full animation capabilities"""

        # Initialize the base animation system with the new parameters
        super().__init__(
            state=state,
            keystates=keystates,
            property_easing=property_easing,
            property_keystates=property_keystates,
            # Removed from super() call: global_transitions, easing, segment_easing
        )

        self.elements = elements if elements else []

    def render(self) -> Optional[dw.Group]:
        """Render the element group in its initial state (static rendering)"""
        return self.render_at_frame_time(0.0)

    def render_at_frame_time(
        self, t: float, drawing: Optional[dw.Drawing] = None
    ) -> Optional[dw.Group]:
        """Render the element transform group at a specific animation time"""

        group_state, _ = self._get_state_at_time(t)

        if group_state is None:
            return None

        transform_string = self._build_transform_string(group_state)

        if transform_string:
            group = dw.Group(transform=transform_string)
        else:
            group = dw.Group()

        for child in self.elements:
            child_element = None
            if hasattr(child, "render_at_frame_time") and child.is_animatable():
                child_element = child.render_at_frame_time(t)
            else:
                child_element = child.render()

            if child_element is not None:
                group.append(child_element)

        if group_state.opacity != 1.0:
            group.opacity = group_state.opacity

        return group

    def _build_transform_string(self, state: VElementGroupState) -> str:
        """Build SVG transform string from state with advanced transform support"""
        transform_parts = []

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

        if state.x != 0 or state.y != 0:
            transform_parts.append(f"translate({state.x}, {state.y})")

        if state.rotation != 0:
            transform_parts.append(f"rotate({state.rotation})")

        if state.scale != 1.0 and (state.scale_x == 1.0 and state.scale_y == 1.0):
            transform_parts.append(f"scale({state.scale})")
        elif state.scale_x != 1.0 or state.scale_y != 1.0:
            final_scale_x = state.scale_x * state.scale
            final_scale_y = state.scale_y * state.scale
            transform_parts.append(f"scale({final_scale_x}, {final_scale_y})")
        elif state.scale != 1.0:
            transform_parts.append(f"scale({state.scale})")

        if state.skew_x != 0:
            transform_parts.append(f"skewX({state.skew_x})")

        if state.skew_y != 0:
            transform_parts.append(f"skewY({state.skew_y})")

        if has_transform_origin and (has_rotation or has_non_uniform_scale or has_skew):
            transform_parts.append(
                f"translate({-state.transform_origin_x}, {-state.transform_origin_y})"
            )

        return " ".join(transform_parts)

    def get_elements(self) -> List[VElement]:
        """Get the list of child elements"""
        return self.elements.copy()

    def add_element(self, child: VElement) -> None:
        """Add a child element to the group"""
        self.elements.append(child)

    def add_elements(self, elements: List[VElement]) -> None:
        """Add multiple child elements to the group"""
        self.elements.extend(elements)

    def remove_element(self, child: VElement) -> None:
        """Remove a child element from the group"""
        if child in self.elements:
            self.elements.remove(child)
        else:
            raise ValueError("Element not found in group")

    def clear_elements(self) -> None:
        """Remove all child elements from the group"""
        self.elements.clear()

    def is_empty(self) -> bool:
        """Check if the group has no child elements"""
        return len(self.elements) == 0
