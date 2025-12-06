# ============================================================================
# vood/components/path_text.py
# ============================================================================
"""PathText component - Text that follows any SVG path with morphing support"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.path_text import PathTextState




class PathTextRenderer(Renderer):
    """Renderer for text along any SVG path with morphing support

    Features:
    - Text follows any SVG path (lines, curves, beziers, etc.)
    - Smooth path morphing between different paths
    - Single or multiple texts along path
    - Custom positioning via offset/offsets

    Examples:
        >>> from vood.paths import line, quadratic_curve
        >>> from vood.components.path_text import PathTextState, PathTextRenderer
        >>>
        >>> # Static text on curved path
        >>> state = PathTextState(
        ...     text="Curved Text",
        ...     path=quadratic_curve(0, 100, 100, 0, 200, 100)
        ... )
        >>> element = VElement(PathTextRenderer(), state=state)
        >>>
        >>> # Morphing path animation
        >>> path1 = line(0, 0, 200, 0)
        >>> path2 = quadratic_curve(0, 0, 100, -50, 200, 0)
        >>> element = VElement(
        ...     renderer=PathTextRenderer(),
        ...     keystates=[
        ...         (0.0, PathTextState(text="Morphing", path=path1)),
        ...         (1.0, PathTextState(text="Morphing", path=path2))
        ...     ]
        ... )
        >>> # Path smoothly morphs from straight to curved!
    """

    def __init__(self) -> None:
        """Initialize path text renderer"""
        pass

    def _render_core(
        self, state: "PathTextState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Group:
        """Render text along the path with the given state (core geometry only)"""

        # Convert SVGPath to drawsvg Path
        path_string = state.data.to_string()
        text_path = dw.Path(
            d=path_string, id=f"text_path_{id(self)}"  # Unique ID for this instance
        )

        # Create a group to hold the text elements
        group = dw.Group()

        if isinstance(state.text, list):
            # Handle multiple texts with custom offsets or even distribution
            texts = state.text
            num_texts = len(texts)

            # Validate offsets if provided
            if state.offsets is not None and len(state.offsets) < num_texts:
                raise ValueError(
                    f"Length of offsets ({len(state.offsets)}) must be equal or bigger "
                    f"than number of texts ({num_texts})"
                )

            for i, text_content in enumerate(texts):
                if state.offsets is not None:
                    # Use custom offset (0.0 to 1.0)
                    text_offset = state.offsets[i]
                else:
                    # Distribute texts evenly along path
                    text_offset = i / max(1, num_texts - 1) if num_texts > 1 else 0.0

                # Apply base offset
                final_offset = (state.offset + text_offset) % 1.0

                text_element = self._create_text_element(
                    text_content, final_offset, text_path, state
                )
                group.append(text_element)
        else:
            # Handle single text
            text_element = self._create_text_element(
                state.text, state.offset, text_path, state
            )
            group.append(text_element)

        return group

    def _create_text_element(
        self,
        text_content: str,
        offset: float,
        text_path: dw.Path,
        state: "PathTextState",
    ) -> dw.Text:
        """Create a single text element at the specified offset along the path

        Args:
            text_content: The text to display
            offset: Position along path (0.0 to 1.0)
            text_path: The path for text to follow
            state: State containing text properties

        Returns:
            drawsvg Text element
        """
        fill_color = state.fill_color.to_rgb_string()
        stroke_color = state.stroke_color.to_rgb_string()

        text_kwargs = {
            "text": text_content,
            "font_family": state.font_family,
            "font_size": state.font_size,
            "font_weight": state.font_weight,
            "text_anchor": state.text_anchor,
            "dominant_baseline": state.dominant_baseline,
            "path": text_path,
            "start_offset": f"{offset * 100}%",
        }
        self._set_fill_and_stroke_kwargs(state, text_kwargs, drawing)


        # Add letter spacing if specified
        if abs(state.letter_spacing) > 1e-10:
            text_kwargs["letter_spacing"] = state.letter_spacing

        # Create text element
        text_element = dw.Text(**text_kwargs)

        # Apply flip transform if needed (for text on bottom of curves)
        if state.flip_text:
            text_element.args["transform"] = "scale(1, -1)"

        return text_element
