"""Abstract base class for renderers with multiple path variants and text labels"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import ABC
from typing import TYPE_CHECKING, Dict, Any

import drawsvg as dw

from .base import Renderer

if TYPE_CHECKING:
    from ..state.path_and_text_variants import PathAndTextVariantsState


class PathAndTextVariantsRenderer(Renderer, ABC):
    """Abstract base class for renderers with multiple path variants and text labels

    Subclasses just need to define PATH_VARIANTS dictionary with:
    - "variant_name": {
        "path": "SVG path data" or ["path1", "path2", ...],
        "text": "LABEL TEXT",
        "text_position": (text_x, text_y),
        "viewbox": original_size,
        "center": (cx, cy)
      }
    """

    # Subclasses must define this
    PATH_VARIANTS: Dict[str, Dict[str, Any]] = {}

    def __init__(self, variant: str = None) -> None:
        """Initialize multi-path text renderer

        Args:
            variant: Path variant name. If None, uses first available variant
        """
        if not self.PATH_VARIANTS:
            raise NotImplementedError("Subclass must define PATH_VARIANTS dictionary")

        # Use first variant as default if none specified
        if variant is None:
            variant = list(self.PATH_VARIANTS.keys())[0]

        if variant not in self.PATH_VARIANTS:
            available = list(self.PATH_VARIANTS.keys())
            raise ValueError(f"Unknown variant '{variant}'. Available: {available}")

        self.variant = variant
        self.data = self.PATH_VARIANTS[variant]

    def _render_core(
        self, state: "PathAndTextVariantsState", drawing: Optional[dw.Drawing] = None
    ) -> dw.Group:
        """Render the renderer geometry only (no transforms or positioning)

        Args:
            state: MultiPathTextState containing rendering properties

        Returns:
            drawsvg Group containing both path(s) and text
        """
        fill_color = state.fill_color.to_rgb_string()
        text_color = (
            state.text_color.to_rgb_string()
            if state.text_color
            else state.fill_color.to_rgb_string()
        )

        # Get the path variant data - can be single path or list of paths
        data = self.data["path"]
        text_content = self.data["text"]
        text_x, text_y = self.data["text_position"]
        viewbox_size = self.data["viewbox"]
        cx, cy = self.data["center"]

        # Create main group to hold everything

        scale_factor = state.size / viewbox_size
        main_group = dw.Group(transform=f"scale({scale_factor}) translate({-cx},{-cy})")

        # Handle multiple paths (if data is a list) or single path
        if isinstance(data, list):
            # Multiple paths - create a group for paths
            path_group = dw.Group()

            for path_string in data:
                # Create path kwargs
                path_kwargs = {"d": path_string}
                self._set_fill_and_stroke_kwargs(state, path_kwargs, drawing)

                # Set opacity
                path_kwargs["opacity"] = state.opacity

                path_group.append(dw.Path(**path_kwargs))

            main_group.append(path_group)
        else:
            # Single path
            path_string = data

            # Create path kwargs
            path_kwargs = {"d": path_string}
            self._set_fill_and_stroke_kwargs(state, path_kwargs, drawing)

            # Set opacity
            path_kwargs["opacity"] = state.opacity

            main_group.append(dw.Path(**path_kwargs))

        # Add text element
        text_kwargs = {
            "x": text_x,
            "y": text_y,
            "text": text_content,
            "font_family": state.font_family,
            "font_size": state.font_size,
            "letter_spacing": state.letter_spacing,
            "font_weight": state.font_weight,
            "fill": text_color,
            "stroke": state.stroke_color.to_rgb_string(),
            "fill_opacity": state.fill_opacity,
            "stroke_opacity": state.stroke_opacity,
            "text_anchor": state.text_align,
            "opacity": state.opacity,
        }

        text = dw.Text(**text_kwargs)

        main_group.append(text)

        return main_group

    @classmethod
    def get_available_variants(cls) -> list[str]:
        """Get list of available variants for this renderer"""
        return list(cls.PATH_VARIANTS.keys())

    def get_current_variant(self) -> str:
        """Get the currently selected variant"""
        return self.variant

    def set_variant(self, variant: str) -> None:
        """Set the current variant

        Args:
            variant: Path variant name to set

        Raises:
            ValueError: If variant is not available
        """
        if variant not in self.PATH_VARIANTS:
            available = list(self.PATH_VARIANTS.keys())
            raise ValueError(f"Unknown variant '{variant}'. Available: {available}")

        self.variant = variant
        self.data = self.PATH_VARIANTS[variant]
