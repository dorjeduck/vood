"""Easing function resolution with 4-level priority system"""

from typing import Callable, Dict, Optional

from vood.component import State
from vood.transition import easing


class EasingResolver:
    """
    Resolves easing functions for property animations using a 4-level priority system.
    
    Priority (highest to lowest):
    1. Segment-level easing overrides (per keystate segment)
    2. Instance-level property easing (property_easing dict)
    3. State class default easing (State.DEFAULT_EASING)
    4. Global default (linear)
    """

    def __init__(
        self,
        property_easing: Optional[Dict[str, Callable[[float], float]]] = None,
    ):
        """
        Initialize the easing resolver.
        
        Args:
            property_easing: Instance-level easing overrides for specific properties
        """
        self.property_easing = property_easing or {}

    def get_easing_for_field(
        self,
        state: State,
        field_name: str,
        segment_easing_overrides: Optional[Dict[str, Callable[[float], float]]] = None,
    ) -> Callable[[float], float]:
        """
        Get the easing function for a field following the 4-level priority.
        
        Args:
            state: The state object containing the field
            field_name: Name of the field being animated
            segment_easing_overrides: Optional segment-level easing overrides
            
        Returns:
            Easing function to apply
        """
        # Level 1: Segment-level override (highest priority)
        if segment_easing_overrides and field_name in segment_easing_overrides:
            return segment_easing_overrides[field_name]

        # Level 2: Instance-level property easing
        if field_name in self.property_easing:
            return self.property_easing[field_name]

        # Level 3: State class default easing
        default_easing = getattr(state, "DEFAULT_EASING", {})
        if field_name in default_easing:
            return default_easing[field_name]

        # Level 4: Global default
        return easing.linear

    def get_easing_for_property_timeline(
        self,
        state: Optional[State],
        field_name: str,
    ) -> Callable[[float], float]:
        """
        Get fallback easing for custom property timelines.
        
        Used when a property timeline segment doesn't specify its own easing.
        Uses instance-level or state-level defaults.
        
        Args:
            state: Optional state object for accessing class defaults
            field_name: Name of the property
            
        Returns:
            Easing function to apply
        """
        # Level 2: Instance-level property easing
        if field_name in self.property_easing:
            return self.property_easing[field_name]

        # Level 3: State class default easing (if state provided)
        if state:
            default_easing = getattr(state, "DEFAULT_EASING", {})
            if field_name in default_easing:
                return default_easing[field_name]

        # Level 4: Global default
        return easing.linear