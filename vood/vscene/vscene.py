from __future__ import annotations

from typing import List, Optional, Union, TYPE_CHECKING, Literal

import drawsvg as dw

from vood.core import get_logger, Color
from vood.config import get_config, ConfigKey

if TYPE_CHECKING:
    from vood.velement import VElement, VElementGroup

# Type alias for any renderable element
RenderableElement = Union["VElement", "VElementGroup"]

logger = get_logger()


class VScene:
    """Manages multiple animated elements and generates frames for animation

    A scene coordinates the rendering of multiple elements at specific time points,
    with support for global transforms and styling.

    Configuration:
        Default values for width, height, and background can be customized via
        vood.toml configuration file. See vood.config documentation.
    """

    def __init__(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        background: Optional[Color] = None,
        background_opacity: Optional[float] = None,
        origin: Optional[Literal["center", "top-left"]] = None,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        scale: float = 1.0,
        rotation: float = 0.0,
    ) -> None:
        """Initialize a new scene with given dimensions and styling

        Args:
            width: Width of the scene in pixels (default: from config, 800)
            height: Height of the scene in pixels (default: from config, 800)
            background: Background color (default: from config, transparent)
            background_opacity: Opacity of the background 0.0-1.0 (default: from config, 1.0)
            origin: Coordinate origin (default: from config, "center")
            offset_x: Global X offset for entire scene
            offset_y: Global Y offset for entire scene
            scale: Global scale factor for entire scene
            rotation: Global rotation in degrees for entire scene
        """
        # Load config for defaults
        config = get_config()

        # Apply config defaults for None values
        if width is None:
            width = config.get(ConfigKey.SCENE_WIDTH, 800)
        if height is None:
            height = config.get(ConfigKey.SCENE_HEIGHT, 800)
        if background is None:
            background = config.get(ConfigKey.SCENE_BACKGROUND_COLOR, Color.NONE)
        if background_opacity is None:
            background_opacity = config.get(ConfigKey.SCENE_BACKGROUND_OPACITY, 1.0)
        if origin is None:
            origin = config.get(ConfigKey.SCENE_ORIGIN_MODE, "center")

        # Validation
        if width <= 0 or height <= 0:
            raise ValueError(f"Width and height must be positive, got {width}x{height}")
        if not 0.0 <= background_opacity <= 1.0:
            raise ValueError(
                f"background_opacity must be 0.0-1.0, got {background_opacity}"
            )

        self.width = width
        self.height = height
        self.origin = origin

        # Parse background color
        if isinstance(background, str) and background.lower() == "none":
            self.background = None
        else:
            self.background = background

        self.background_opacity = background_opacity

        # Global transforms
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale = scale
        self.rotation = rotation

        # Elements list
        self.elements: List[RenderableElement] = []

    # ========================================================================
    # Element Management
    # ========================================================================

    def add_element(self, element: RenderableElement) -> None:
        """Add an element or group to the scene

        Args:
            element: The element or group to add to the scene
        """
        self.elements.append(element)

    def add_elements(self, elements: List[RenderableElement]) -> None:
        """Add multiple elements or groups to the scene

        Args:
            elements: List of elements or groups to add to the scene
        """
        self.elements.extend(elements)

    def remove_element(self, element: RenderableElement) -> bool:
        """Remove specific element from scene

        Args:
            element: The element to remove

        Returns:
            True if element was found and removed, False otherwise
        """
        try:
            self.elements.remove(element)
            return True
        except ValueError:
            return False

    def clear_elements(self) -> None:
        """Remove all elements from scene"""
        self.elements.clear()

    def element_count(self) -> int:
        """Get total number of elements in scene"""
        return len(self.elements)

    def animatable_element_count(self) -> int:
        """Get number of elements that have animation"""
        return sum(1 for e in self.elements if e.is_animatable())

    # ========================================================================
    # Rendering
    # ========================================================================

    def to_drawing(
        self,
        frame_time: float = 0.0,
        render_scale: float = 1.0,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> dw.Drawing:
        """Render the scene as a drawsvg Drawing object at specified time.

        Useful for video encoding or when you need the Drawing object
        directly without converting to SVG string.

        Args:
            frame_time: Time point to render (0.0 to 1.0)
            render_scale: Additional scale factor for rendering (multiplies scene scale)
            width: Optional width override (in pixels)
            height: Optional height override (in pixels)

        Returns:
            dw.Drawing object

        Raises:
            ValueError: If frame_time is outside [0.0, 1.0]
        """
        # Validation
        if not 0.0 <= frame_time <= 1.0:
            raise ValueError(
                f"frame_time must be between 0.0 and 1.0, got {frame_time}"
            )

        # Calculate final dimensions
        ww = width if width is not None else render_scale * self.width
        hh = height if height is not None else render_scale * self.height

        drawing = dw.Drawing(ww, hh, origin=self.origin)

        # Add background
        if self.background is not None and self.background_opacity > 0.0:
            # Calculate background position based on origin
            if self.origin == "center":
                bg_x, bg_y = -ww / 2, -hh / 2
            else:  # top-left
                bg_x, bg_y = 0, 0

            drawing.append(
                dw.Rectangle(
                    bg_x,
                    bg_y,
                    ww,
                    hh,
                    fill=self.background.to_rgb_string(),
                    fill_opacity=self.background_opacity,
                )
            )

        # Create global transform group
        transform = self._build_transform(render_scale)
        group = dw.Group(transform=transform) if transform else dw.Group()

        # Add all elements at specified time
        for element in self.elements:
            rendered = element.render_at_frame_time(frame_time, drawing=drawing)
            if rendered is not None:
                group.append(rendered)

        drawing.append(group)
        return drawing

    def to_svg(
        self,
        frame_time: float = 0.0,
        render_scale: float = 1.0,
        width: Optional[float] = None,
        height: Optional[float] = None,
        filename: Optional[str] = None,
        log: bool = True,
    ) -> str:
        """Render the scene to SVG string at specified time.

        Args:
            frame_time: Time point to render (0.0 to 1.0)
            render_scale: Additional scale factor for rendering
            width: Optional width override (in pixels)
            height: Optional height override (in pixels)
            filename: Optional filename to save SVG to
            log: Whether to log the save operation

        Returns:
            SVG string

        Raises:
            ValueError: If frame_time is outside [0.0, 1.0]
        """
        drawing = self.to_drawing(
            frame_time=frame_time,
            render_scale=render_scale,
            width=width,
            height=height,
        )

        svg_string = drawing.as_svg()

        if filename:
            drawing.save_svg(filename)
            if log:
                logger.info(f"Scene saved to {filename} at t={frame_time}")

        return svg_string

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _build_transform(self, render_scale: float) -> str:
        """Build SVG transform string from scene transforms

        Args:
            render_scale: Additional scale factor for rendering

        Returns:
            SVG transform string, or empty string if no transforms needed
        """
        transforms = []

        # Combine scene scale with render scale
        total_scale = self.scale * render_scale
        if total_scale != 1.0:
            transforms.append(f"scale({total_scale})")

        # Add rotation if present
        if self.rotation != 0.0:
            transforms.append(f"rotate({self.rotation})")

        # Add translation if present
        if self.offset_x != 0.0 or self.offset_y != 0.0:
            transforms.append(f"translate({self.offset_x},{self.offset_y})")

        return " ".join(transforms)

    def get_animation_time_range(self) -> tuple[float, float]:
        """Get the time range covered by all elements

        Returns the minimum start time and maximum end time across all
        elements that have keystates.

        Returns:
            Tuple of (min_time, max_time). Returns (0.0, 1.0) if no elements have keystates.
        """
        if not self.elements:
            return (0.0, 1.0)

        times = []
        for element in self.elements:
            if hasattr(element, "keystates") and element.keystates:
                times.append(element.keystates[0].time)  # First keystate time
                times.append(element.keystates[-1].time)  # Last keystate time

        if not times:
            return (0.0, 1.0)

        return (min(times), max(times))

    # ========================================================================
    # Convenience Properties
    # ========================================================================

    @property
    def dimensions(self) -> tuple[float, float]:
        """Get scene dimensions as (width, height)"""
        return (self.width, self.height)

    @property
    def aspect_ratio(self) -> float:
        """Get scene aspect ratio (width / height)"""
        return self.width / self.height

    # ========================================================================
    # Jupyter Notebook Display
    # ========================================================================

    def _repr_svg_(self):
        """Display in Jupyter notebook (auto-called by Jupyter)."""
        from vood.vscene.preview import PreviewRenderer
        return PreviewRenderer(self).repr_svg()

    def display_inline(self, frame_time: float = 0.0):
        """Display inline in the Jupyter web page.

        Args:
            frame_time: Time point to render (0.0 to 1.0)

        Returns:
            JupyterSvgInline object that displays in notebooks
        """
        from vood.vscene.preview import PreviewRenderer
        return PreviewRenderer(self).display_inline(frame_time)

    def display_iframe(self, frame_time: float = 0.0):
        """Display within an iframe in the Jupyter web page.

        Args:
            frame_time: Time point to render (0.0 to 1.0)

        Returns:
            JupyterSvgFrame object that displays in notebooks
        """
        from vood.vscene.preview import PreviewRenderer
        return PreviewRenderer(self).display_iframe(frame_time)

    def display_image(self, frame_time: float = 0.0):
        """Display within an img tag in the Jupyter web page.

        Args:
            frame_time: Time point to render (0.0 to 1.0)

        Returns:
            JupyterSvgImage object that displays in notebooks
        """
        from vood.vscene.preview import PreviewRenderer
        return PreviewRenderer(self).display_image(frame_time)

    def preview_grid(self, num_frames: int = 10, scale: float = 1.0):
        """Preview animation by showing all frames in a grid layout.

        Useful for quickly checking animations in Jupyter without video export.
        Shows all frames at once for easy visual comparison.

        Args:
            num_frames: Number of frames to display (default: 10)
            scale: Scale factor for frame size, e.g. 0.5 for half size (default: 1.0)

        Returns:
            HTML object that displays in Jupyter notebooks
        """
        from vood.vscene.preview import PreviewRenderer
        return PreviewRenderer(self).preview_grid(num_frames, scale)

    def preview_animation(self, num_frames: int = 10, play_interval_ms: int = 100):
        """Preview animation with interactive controls (play/pause, slider, prev/next).

        Useful for checking animations in Jupyter without video export.
        Shows one frame at a time with playback controls.

        Args:
            num_frames: Number of frames to display (default: 10)
            play_interval_ms: Milliseconds between frames when playing (default: 100)

        Returns:
            HTML object that displays in Jupyter notebooks
        """
        from vood.vscene.preview import PreviewRenderer
        return PreviewRenderer(self).preview_animation(num_frames, play_interval_ms)

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"VScene(width={self.width}, height={self.height}, "
            f"elements={len(self.elements)}, "
            f"animatable={self.animatable_element_count()})"
        )
