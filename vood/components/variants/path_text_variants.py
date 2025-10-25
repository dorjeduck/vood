"""Abstract base class for renderers with multiple path variants and text labels"""

from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Any

import drawsvg as dw

from vood.components import Renderer, State
from vood.utils import to_rgb_string
from vood.transitions import Easing


@dataclass
class MultiPathTextState(State):
    """Base state class for multi-path renderers with text labels"""

    size: float = 500
    color: Tuple[int, int, int] = (255, 0, 0)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0

    # Text properties
    font_size: float = 35
    letter_spacing: float = 0
    font_family: str = "Comfortaa"
    text_align: str = "left"
    font_weight: str = "normal"
    text_color: Optional[Tuple[int, int, int]] = (
        None  # If None, uses same as renderer color
    )

    DEFAULT_EASING = {
        "x": Easing.in_out,
        "y": Easing.in_out,
        "scale": Easing.in_out,
        "rotation": Easing.in_out,
        "opacity": Easing.linear,
        "size": Easing.in_out,
        "color": Easing.linear,
        "stroke_color": Easing.linear,
        "stroke_width": Easing.in_out,
        "font_size": Easing.in_out,
        "letter_spacing": Easing.in_out,
        "font_family": Easing.linear,
        "text_align": Easing.linear,
        "font_weight": Easing.linear,
        "text_color": Easing.linear,
    }


class MultiPathTextRenderer(Renderer, ABC):
    """Abstract base class for renderers with multiple path variants and text labels

    Subclasses just need to define PATH_VARIANTS dictionary with:
    - "variant_name": {
        "path": "SVG path data" or ["path1", "path2", ...],
        "text": "LABEL TEXT",
        "text_position": (text_x, text_y),
        "viewbox": original_size,
        "center": (center_x, center_y)
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
        self.path_data = self.PATH_VARIANTS[variant]

    def _render_core(self, state: MultiPathTextState) -> dw.Group:
        """Render the renderer geometry only (no transforms or positioning)

        Args:
            state: MultiPathTextState containing rendering properties

        Returns:
            drawsvg Group containing both path(s) and text
        """
        fill_color = to_rgb_string(state.color)
        text_color = to_rgb_string(
            state.text_color if state.text_color else state.color
        )

        # Get the path variant data - can be single path or list of paths
        path_data = self.path_data["path"]
        text_content = self.path_data["text"]
        text_x, text_y = self.path_data["text_position"]
        viewbox_size = self.path_data["viewbox"]
        center_x, center_y = self.path_data["center"]

        # Create main group to hold everything

        scale_factor =  state.size / viewbox_size
        main_group = dw.Group(
            transform=f"scale({scale_factor}) translate({-center_x},{-center_y})"
        )

        # Handle multiple paths (if path_data is a list) or single path
        if isinstance(path_data, list):
            # Multiple paths - create a group for paths
            path_group = dw.Group()

            for path_string in path_data:
                # Create path kwargs
                path_kwargs = {
                    "d": path_string,
                    "fill": fill_color,
                }

                # Add stroke if specified
                if state.stroke_color and state.stroke_width > 0:
                    path_kwargs["stroke"] = to_rgb_string(state.stroke_color)
                    path_kwargs["stroke_width"] = state.stroke_width

                # Set opacity
                path_kwargs["opacity"] = state.opacity

                path_group.append(dw.Path(**path_kwargs))

            main_group.append(path_group)
        else:
            # Single path
            path_string = path_data

            # Create path kwargs
            path_kwargs = {
                "d": path_string,
                "fill": fill_color,
            }

            # Add stroke if specified
            if state.stroke_color and state.stroke_width > 0:
                path_kwargs["stroke"] = to_rgb_string(state.stroke_color)
                path_kwargs["stroke_width"] = state.stroke_width

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
        self.path_data = self.PATH_VARIANTS[variant]
