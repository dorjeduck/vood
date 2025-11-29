from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.circle_text import CircleTextState




class CircleTextRenderer(Renderer):
    """Renderer class for rendering text elements"""

    def __init__(
        self,
    ) -> None:
        """Initialize text renderer

        Args:
            text: The text content to display - either single string or list of strings
            text_facing_inward: Whether text faces inward (True, default) or outward (False)
            angles: Optional list of specific angles in degrees for each text element.
                   If provided, overrides automatic even distribution.
                   List length should match text length for multi-text.
        """

    def _render_core(
        self, state: "CircleTextState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Group:
        """Render the circular text with the given state (core geometry only)"""

        # Create the circular path that text will follow
        circle_path = self._create_circle_path(
            text_facing_inward=state.text_facing_inward,
            radius=state.radius,
            path_id=f"circle_path_{id(self)}",  # Unique ID for this instance
        )

        # Create a group to hold the text elements
        group = dw.Group()

        if isinstance(state.text, list):
            # Handle multiple texts with custom angles or even distribution
            texts = state.text
            num_texts = len(texts)

            # Validate angles if provided
            if state.angles is not None and len(state.angles) < num_texts:
                raise ValueError(
                    f"Length of angles ({len(state.angles)}) must be equal or bigger than number of texts ({num_texts})"
                )

            for i, text_content in enumerate(texts):
                if state.angles is not None:
                    # Use custom angle - convert degrees to fraction of circle (0-1 range)
                    angle_fraction = (state.angles[i] % 360) / 360
                    text_position = state.rotation / 360 + angle_fraction
                else:
                    # Distribute texts evenly around one full circle (0 to 1 range)
                    text_position = state.rotation / 360 + (i / num_texts)

                text_element = self._create_text_element(
                    text_content, text_position, circle_path, state
                )
                group.append(text_element)
        else:
            # Handle single text (original behavior)
            text_element = self._create_text_element(
                state.text, state.rotation, circle_path, state
            )
            group.append(text_element)

        return group

    def _create_circle_path(
        self,
        text_facing_inward: bool,
        radius: float,
        path_id: str = "circlepath",
    ) -> dw.Path:
        """Create a circular path for text to follow

        Args:
            radius: Radius of the circle
            path_id: ID for the path element

        Returns:
            drawsvg Path object representing a circle (goes around twice)
        """
        # Create circular path that goes around twice: 6→12→6→12→6
        # Start at bottom (6 o'clock), go up to top (12 o'clock), back down, up again, back down
        # This provides plenty of path length so text is never cut off
        # Arc direction determines text facing: clockwise (0,1) = inward, counter-clockwise (0,0) = outward
        arc_direction = "1" if text_facing_inward else "0"
        d_attr = (
            f"M 0,{radius} "  # Start at bottom (6 o'clock)
            f"A {radius},{radius} 0 0,{arc_direction} 0,{-radius} "  # First half: 6→12
            f"A {radius},{radius} 0 0,{arc_direction} 0,{radius} "  # Second half: 12→6
            f"A {radius},{radius} 0 0,{arc_direction} 0,{-radius} "  # Third half: 6→12
            f"A {radius},{radius} 0 0,{arc_direction} 0,{radius}"  # Fourth half: 12→6
        )
        return dw.Path(d=d_attr, id=path_id)

    def _create_text_element(
        self,
        text_content: str,
        offset: float,
        circle_path: dw.Path,
        state: "CircleTextState",
    ) -> dw.Text:
        """Create a single text element at the specified offset

        Args:
            text_content: The text to display
            offset: Position offset (0-1 range)
            circle_path: The circular path for text to follow
            state: State containing text properties

        Returns:
            drawsvg Text element
        """

        fill_color = state.fill_color.to_rgb_string()

        # Map offset to path coordinates
        mapped_offset = 0.25 + (offset * 0.5)

        text_kwargs = {
            "text": text_content,
            "font_family": state.font_family,
            "font_size": state.font_size,
            "font_weight": state.font_weight,
            "letter_spacing": state.letter_spacing,
            "fill": fill_color,
            "text_anchor": state.text_align,
            "path": circle_path,
            "start_offset": f"{mapped_offset*100}%",
            "text_anchor": state.text_anchor,
            "dominant_baseline": state.dominant_baseline,
        }

        # Add letter spacing if specified
        if abs(state.letter_spacing) > 1e-10:
            text_kwargs["letter_spacing"] = state.letter_spacing

        return dw.Text(**text_kwargs)
