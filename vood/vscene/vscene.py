from __future__ import annotations

from typing import List, Optional, Union, TYPE_CHECKING

import drawsvg as dw

from vood.utils import get_logger

if TYPE_CHECKING:
    from vood.velements import VElement, VElementGroup

# Type alias for any renderable element
RenderableElement = Union["VElement", "VElementGroup"]

# Note: Legacy classes removed - only Element is supported now

logger = get_logger()
# ============================================================================
# SCENE GENERATOR
# ============================================================================


class VScene:
    """Manages multiple animated elements and generates frames for animation"""

    def __init__(
        self,
        width: float = 800,
        height: float = 800,
        background: str = "white",
        background_opacity: float = 1.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        scale: float = 1.0,
        rotation: float = 0.0,
    ) -> None:
        """Initialize a new scene with given dimensions and background

        Args:
            width: Width of the scene in pixels
            height: Height of the scene in pixels
            background: Background color as CSS color string
            background_opacity: Opacity of the background (0.0 to 1.0)
        """
        self.width = width
        self.height = height
        self.background = background
        self.background_opacity = background_opacity

        self.elements: List[RenderableElement] = []
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale = scale
        self.rotation = rotation

    def add_element(self, element: RenderableElement) -> None:
        """Add an element or container to the scene

        Args:
            element: The element or container to add to the scene
        """
        self.elements.append(element)

    def add_elements(self, elements: List[RenderableElement]) -> None:
        """Add elements or ElementTransformGroups to the scene

        Args:
            elements: The element or ElementTransformGroups to add to the scene
        """
        for element in elements:
            self.elements.append(element)

    def to_drawing(
        self,
        frame_time: float = 0.0,
        scale: float = 1.0,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> dw.Drawing:
        """
        Render the scene as a drawsvg Drawing object at specified time.

        Useful for video encoding or when you need the Drawing object
        directly without converting to SVG string.

        Args:
            frame_time: Time point to render (0.0 to 1.0)
            scale: Scale factor for the scene
            width: Optional width override
            height: Optional height override

        Returns:
            dw.Drawing object
        """
        ww = width if width is not None else scale * self.width
        hh = height if height is not None else scale * self.height

        drawing = dw.Drawing(ww, hh, origin="center")

        # Add background
        if self.background_opacity > 0.0 and self.background not in (None, "none"):
            drawing.append(
                dw.Rectangle(
                    -ww / 2,
                    -hh / 2,
                    ww,
                    hh,
                    fill=self.background,
                    fill_opacity=self.background_opacity,
                )
            )

        # Create global transform group
        transform = ""
        if self.scale * scale != 1.0:
            transform += f"scale({self.scale*scale}) "
        if self.rotation != 0.0:
            transform += f"rotate({self.rotation}) "
        if self.offset_x != 0.0 or self.offset_y != 0.0:
            transform += f"translate({self.offset_x},{self.offset_y}) "

        if transform:
            group = dw.Group(transform=transform.strip())
        else:
            group = dw.Group()

        # Add all elements at specified time
        for element in self.elements:
            rendered = element.render_at_frame_time(frame_time)
            group.append(rendered)

        drawing.append(group)
        return drawing

    def to_svg(
        self,
        frame_time: float = 0.0,
        scale: float = 1.0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        filename: Optional[str] = None,
        log: bool = True,
    ) -> str:
        """
        Render the scene to SVG string at specified time.

        Args:
            frame_time: Time point to render (0.0 to 1.0)
            scale: Scale factor for the scene
            width: Optional width override
            height: Optional height override
            filename: Optional filename to save SVG to
            log: Whether to log the save operation

        Returns:
            SVG string
        """
        # Reuse to_drawing to avoid duplication
        drawing = self.to_drawing(
            frame_time=frame_time, scale=scale, width=width, height=height
        )

        svg_string = drawing.as_svg()

        if filename:
            drawing.save_svg(filename)
            if log:
                logger.info(f"Scene saved to {filename} at t={frame_time}")

        return svg_string
