"""Abstract base class for renderers with multiple path variants"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Any

import drawsvg as dw

from vood.components import Renderer, State
from vood.utils import to_rgb_string
from vood.transitions import Easing


@dataclass
class PathVariantState(State):
    """Base state class for multi-path renderers"""

    size: float = 50
    color: Tuple[int, int, int] = (255, 0, 0)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 0
    case_sensitive: bool = False

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
    }


class PathVariantRenderer(Renderer, ABC):
    """Abstract base class for renderers with multiple path variants

    Subclasses just need to define PATH_VARIANTS dictionary with:
    - "variant_name": {
        "path": "SVG path data",
        "viewbox": original_size,
        "center": (center_x, center_y)
      }
    """

    # Subclasses must define this
    PATH_VARIANTS: Dict[str, Dict[str, Any]] = {}

    def __init__(self, variant: str = None) -> None:
        """Initialize multi-path renderer

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

    def _render_core(self, state: PathVariantState) -> dw.Group:
        """Render the renderer geometry centered at (0,0), no scaling or transforms"""
        fill_color = to_rgb_string(state.color)
        path_data = self.path_data["path"]

        center_x, center_y = self.path_data["center"]

        viewbox_size = self.path_data["viewbox"]
        scale_factor = state.size / viewbox_size
        group = dw.Group(
            transform=f"scale({scale_factor}) translate({-center_x},{-center_y})"
        )

        paths = path_data if isinstance(path_data, list) else [path_data]
        for path_string in paths:
            path_kwargs = {
                "d": path_string,
                "fill": fill_color,
            }
            if state.stroke_color and state.stroke_width > 0:
                path_kwargs["stroke"] = to_rgb_string(state.stroke_color)
                path_kwargs["stroke_width"] = state.stroke_width

            group.append(dw.Path(**path_kwargs))
        group.transform = f"translate({-center_x},{-center_y})"
        return group

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
