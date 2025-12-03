"""Abstract base classes for renderers and states in the vood framework"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
from dataclasses import replace

if TYPE_CHECKING:
    from vood.component.state.base import State

import drawsvg as dw


class Renderer(ABC):
    """Abstract base class for all renderer classes

    Each renderer must implement core geometry in _render_core.
    The base render method applies transforms and opacity.
    """

    @abstractmethod
    def _render_core(
        self, state: State, drawing: Optional[dw.Drawing] = None
    ) -> dw.DrawingElement:
        """Render the shape itself (without transforms)

        Args:
            state: State to render
            drawing: Optional Drawing object for accessing defs section

        Subclasses must implement this method.
        """
        pass

    def render(
        self, state: State, drawing: Optional[dw.Drawing] = None
    ) -> dw.DrawingElement:
        elem = self._render_core(state, drawing=drawing)

        # Apply clipping/masking before transforms
        elem = self._apply_clipping_and_masking(elem, state, drawing)

        transforms = []
        # SVG applies transforms right-to-left, so order is: translate, rotate, scale
        if state.x != 0 or state.y != 0:
            transforms.append(f"translate({state.x},{state.y})")
        if state.rotation != 0:
            transforms.append(f"rotate({state.rotation})")
        if state.scale != 1.0:
            transforms.append(f"scale({state.scale})")

        if transforms:
            elem.args["transform"] = " ".join(transforms)

        elem.args["opacity"] = str(state.opacity)

        return elem

    def _apply_clipping_and_masking(
        self, elem: dw.DrawingElement, state: State, drawing: dw.Drawing
    ) -> dw.DrawingElement:
        """Apply clip-path and mask to element based on state

        Handles:
        - Single clip (clip_state)
        - Multiple clips (clip_states) via nested groups
        - Single mask (mask_state)
        - Combination of clip + mask

        Args:
            elem: The rendered element to clip
            state: State containing clip/mask definitions
            drawing: Drawing for adding defs

        Returns:
            Element wrapped in groups with clipping/masking applied
        """

        result = elem

        # Normalize mask_state/mask_states to list
        if state.mask_state is not None:
            mask_states = [state.mask_state]
        elif state.mask_states is not None:
            mask_states = state.mask_states
        else:
            mask_states = []

        # Normalize clip_state/clip_states to list
        if state.clip_state is not None:
            clip_states = [state.clip_state]
        elif state.clip_states is not None:
            clip_states = state.clip_states
        else:
            clip_states = []

        # Apply masks first (innermost)
        for mask_state in mask_states:
            mask_id = self._create_mask_def(mask_state, drawing)
            masked_group = dw.Group(mask=f"url(#{mask_id})")
            masked_group.append(result)
            result = masked_group

        # Apply clips
        if len(clip_states) > 0:
            clip_id = self._create_clip_path_def(clip_states, drawing)
            clipped_group = dw.Group(clip_path=f"url(#{clip_id})")
            clipped_group.append(result)
            result = clipped_group

        return result

    def _create_clip_path_def(
        self, clip_states: List[State], drawing: dw.Drawing
    ) -> str:
        """Create ClipPath def from a state and add to drawing

        Args:
            clip_states:  List of states defining the clip shape
            drawing: Drawing to add def to

        Returns:
            ID of the created ClipPath def
        """
        import uuid
        from vood.component import get_renderer_instance_for_state
        from vood.component.renderer.base_vertex import VertexRenderer

        # Generate unique ID
        clip_id = f"clip-{uuid.uuid4().hex[:8]}"

        # Create ClipPath container
        clip_path = dw.ClipPath(id=clip_id, clipPathUnits="userSpaceOnUse")

        for clip_state in clip_states:
            # For clipPaths, ensure the state has a fill (color doesn't matter for clipping)
            from vood.core.color import Color
            if not hasattr(clip_state, 'fill_color') or clip_state.fill_color == Color.NONE:
                clip_state = replace(clip_state, fill_color=Color("#000000"))

            # Check if this is a morph state (has _aligned_contours from interpolation)
            if hasattr(clip_state, '_aligned_contours') and clip_state._aligned_contours is not None:
                # This is an interpolated state between different shape types
                # Use VertexRenderer for morphing
                renderer = VertexRenderer()
            else:
                # Normal state - use its registered renderer
                renderer = get_renderer_instance_for_state(clip_state)

            # Use _render_core to get just the shape without wrapper group
            # (clipPaths can't have <g> elements in Chrome)
            clip_elem = renderer._render_core(clip_state, drawing=drawing)

            # Apply transforms directly to the clip element if needed
            transforms = []
            if clip_state.x != 0 or clip_state.y != 0:
                transforms.append(f"translate({clip_state.x},{clip_state.y})")
            if clip_state.rotation != 0:
                transforms.append(f"rotate({clip_state.rotation})")
            if clip_state.scale != 1.0:
                transforms.append(f"scale({clip_state.scale})")

            # Extract paths from group if needed (VertexRenderer returns a group)
            if isinstance(clip_elem, dw.Group) and hasattr(clip_elem, 'children'):
                for child in clip_elem.children:
                    if transforms:
                        child.args["transform"] = " ".join(transforms)
                    clip_path.append(child)
            else:
                if transforms:
                    clip_elem.args["transform"] = " ".join(transforms)
                clip_path.append(clip_elem)


        # Add to drawing's defs
        drawing.append_def(clip_path)

        return clip_id

    def _create_mask_def(self, mask_state: State, drawing: dw.Drawing) -> str:
        """Create Mask def from a state and add to drawing

        Masks use opacity/grayscale for gradual transparency.
        White = fully visible, black = fully transparent.

        Args:
            mask_state: State defining the mask shape
            drawing: Drawing to add def to

        Returns:
            ID of the created Mask def
        """
        import uuid
        from vood.component import get_renderer_instance_for_state
        from vood.component.renderer.base_vertex import VertexRenderer

        # Generate unique ID
        mask_id = f"mask-{uuid.uuid4().hex[:8]}"

        # Create Mask container
        mask = dw.Mask(id=mask_id)

        # For masks, ensure the state has a fill (masks use white for visible areas)
        from vood.core.color import Color
        if not hasattr(mask_state, 'fill_color') or mask_state.fill_color == Color.NONE:
            mask_state = replace(mask_state, fill_color=Color("#FFFFFF"))

        # Check if this is a morph state (has _aligned_contours from interpolation)
        if hasattr(mask_state, '_aligned_contours') and mask_state._aligned_contours is not None:
            # This is an interpolated state between different shape types
            # Use VertexRenderer for morphing
            renderer = VertexRenderer()
        else:
            # Normal state - use its registered renderer
            renderer = get_renderer_instance_for_state(mask_state)

        # Use _render_core to get just the shape
        mask_elem = renderer._render_core(mask_state, drawing=drawing)

        # Extract paths from group if needed (VertexRenderer returns a group)
        if isinstance(mask_elem, dw.Group) and hasattr(mask_elem, 'children'):
            elements = list(mask_elem.children)
        else:
            elements = [mask_elem]

        # Apply transforms and opacity directly
        transforms = []
        if mask_state.x != 0 or mask_state.y != 0:
            transforms.append(f"translate({mask_state.x},{mask_state.y})")
        if mask_state.rotation != 0:
            transforms.append(f"rotate({mask_state.rotation})")
        if mask_state.scale != 1.0:
            transforms.append(f"scale({mask_state.scale})")

        if transforms or mask_state.opacity != 1.0:
            mask_group = dw.Group(opacity=mask_state.opacity)
            if transforms:
                mask_group.args["transform"] = " ".join(transforms)
            for elem in elements:
                mask_group.append(elem)
            mask.append(mask_group)
        else:
            for elem in elements:
                mask.append(elem)

        # Add to drawing's defs
        drawing.append_def(mask)

        return mask_id
