"""Image renderer implementation using new architecture"""

from __future__ import annotations
from typing import Optional

from typing import Tuple

from PIL import Image
import logging
import drawsvg as dw
import random
import io

from .base import Renderer
from ..registry import register_renderer
from ..state.image import ImageState, ImageFitMode


@register_renderer(ImageState)
class ImageRenderer(Renderer):
    """Renderer class for rendering image elements"""

    def _apply_random_transforms(self, img: Image.Image) -> Image.Image:
        """Apply random rotation and flips to image for diversity

        Args:
            img: PIL Image to transform

        Returns:
            Transformed PIL Image
        """
        # Random 90-degree rotation (0, 90, 180, or 270 degrees)
        rotation_choice = random.choice(
            [None, Image.ROTATE_90, Image.ROTATE_180, Image.ROTATE_270]
        )
        if rotation_choice is not None:
            img = img.transpose(rotation_choice)

        # Random horizontal flip (50% chance)
        if random.random() > 0.5:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

        # Random vertical flip (50% chance)
        if random.random() > 0.5:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

        return img

    def _random_crop_image(
        self, href: str, target_width: int, target_height: int
    ) -> Tuple[bytes, str]:
        """Randomly crop and transform an image to fit target dimensions

        Args:
            href: Path to the image file
            target_width: Desired crop width
            target_height: Desired crop height

        Returns:
            Tuple of (image_data_bytes, mime_type)
        """
        with Image.open(href) as img:
            img_width, img_height = img.size

            # Ensure crop dimensions don't exceed image dimensions
            crop_width = min(int(target_width), img_width)
            crop_height = min(int(target_height), img_height)

            if crop_width < img_width or crop_height < img_height:
                # Random crop coordinates
                left = random.randint(0, img_width - crop_width)
                top = random.randint(0, img_height - crop_height)
                right = left + crop_width
                bottom = top + crop_height

                # Crop the image
                img = img.crop((left, top, right, bottom))
            else:
                logging.warning(
                    f"Image {href} ({img_width}x{img_height}) is smaller than target crop size ({target_width}x{target_height}). Using full image."
                )

            # Apply random transformations for diversity
            img = self._apply_random_transforms(img)

            # Save to bytes buffer
            buffer = io.BytesIO()
            # Preserve original format if possible
            img_format = img.format if img.format else "PNG"
            img.save(buffer, format=img_format)
            image_data = buffer.getvalue()

            # Determine mime type
            import mimetypes

            mime_type, _ = mimetypes.guess_type(href)
            if mime_type is None:
                mime_type = "image/png"

            return image_data, mime_type

    def _calculate_dimensions(
        self,
        href: str,
        target_width: float,
        target_height: float,
        original_width: int,
        original_height: int,
        fit_mode: ImageFitMode,
    ) -> Tuple[float, float, bool]:
        """Calculate final image dimensions based on fit mode

        Args:
            target_width: Desired width from state
            target_height: Desired height from state
            original_width: Original image width in pixels
            original_height: Original image height in pixels

        Returns:
            Tuple of (final_width, final_height, needs_clipping)
        """
        import logging

        if fit_mode == ImageFitMode.FIT:
            # Scale to fit entirely within bounds (preserve aspect ratio)
            scale_x = target_width / original_width
            scale_y = target_height / original_height
            scale = min(scale_x, scale_y)
            return (original_width * scale, original_height * scale, False)

        elif fit_mode == ImageFitMode.FILL:
            # Scale to fill bounds completely, crop if needed (preserve aspect ratio)
            scale_x = target_width / original_width
            scale_y = target_height / original_height
            scale = max(scale_x, scale_y)
            return (original_width * scale, original_height * scale, True)

        elif fit_mode == ImageFitMode.CROP:
            # Keep original size, crop to bounds
            return (original_width, original_height, True)

        elif fit_mode == ImageFitMode.STRETCH:
            # Stretch to exact dimensions (changes aspect ratio)
            logging.warning(
                f"Image {self.state.href} aspect ratio will be changed due to STRETCH mode"
            )
            return (target_width, target_height, False)

        elif fit_mode == ImageFitMode.ORIGINAL:
            # Keep original size, warn if doesn't fit
            if original_width > target_width or original_height > target_height:
                logging.warning(
                    f"Image {href} ({original_width}x{original_height}) is larger than target size ({target_width}x{target_height})"
                )
            elif original_width < target_width or original_height < target_height:
                logging.warning(
                    f"Image {href} ({original_width}x{original_height}) is smaller than target size ({target_width}x{target_height})"
                )
            return (original_width, original_height, False)

        elif fit_mode == ImageFitMode.RANDOM_CROP:
            # Random crop will be handled in _render_core
            # Return target dimensions, no clipping needed (image will already be cropped)
            return (target_width, target_height, False)

        else:
            # Default to FIT mode
            scale_x = target_width / original_width
            scale_y = target_height / original_height
            scale = min(scale_x, scale_y)
            return (original_width * scale, original_height * scale, False)

    def _render_core(self, state: ImageState, drawing: Optional[dw.Drawing] = None) -> dw.Group:
        """Render the image renderer without transforms

        Args:
            state: ImageState containing rendering properties

        Returns:
            drawsvg Group containing the image renderer
        """

        # Create a group to hold the image
        group = dw.Group()

        # Read image data for embedding first to get original dimensions
        try:
            import mimetypes

            # Get original image dimensions first
            try:
                with Image.open(state.href) as img:
                    original_width, original_height = img.size
            except ImportError:
                logging.warning(
                    "PIL (Pillow) not available. Cannot determine original image size."
                )
                # If no PIL and no dimensions specified, use reasonable defaults
                original_width, original_height = 100, 100

            # Use original dimensions if width/height not specified in state
            target_width = state.width if state.width is not None else original_width
            target_height = (
                state.height if state.height is not None else original_height
            )

            # Handle RANDOM_CROP mode with special processing
            if state.fit_mode == ImageFitMode.RANDOM_CROP:
                try:
                    image_data, mime_type = self._random_crop_image(
                        state.href, int(target_width), int(target_height)
                    )
                except Exception as e:
                    logging.error(f"Failed to apply random crop to {state.href}: {e}")
                    # Fall back to regular image loading
                    with open(state.href, "rb") as image_file:
                        image_data = image_file.read()
                    mime_type, _ = mimetypes.guess_type(state.href)
                    if mime_type is None:
                        mime_type = "image/png"
            else:
                # Regular image loading for other modes
                with open(state.href, "rb") as image_file:
                    image_data = image_file.read()

                mime_type, _ = mimetypes.guess_type(state.href)
                if mime_type is None:
                    mime_type = "image/png"

            # Calculate final dimensions based on fit mode
            final_width, final_height, clip_rect = self._calculate_dimensions(
                state.href,
                target_width,
                target_height,
                original_width,
                original_height,
                state.fit_mode,
            )

            # Position image based on final dimensions
            final_image_x = -final_width / 2
            final_image_y = -final_height / 2

            image_kwargs = {
                "x": final_image_x,
                "y": final_image_y,
                "width": final_width,
                "height": final_height,
                "opacity": state.opacity,
                "data": image_data,  # Pass raw bytes - drawsvg will handle base64 encoding
                "mime_type": mime_type,
            }

            # Add clipping if needed for CROP or FILL modes
            if clip_rect:
                import uuid

                clip_id = f"clip_{uuid.uuid4().hex[:8]}"

                clip_path = dw.ClipPath()
                clip_path.args["id"] = clip_id

                # Clip rectangle should be the target bounds, centered
                clip_rect_elem = dw.Rectangle(
                    x=-target_width / 2,
                    y=-target_height / 2,
                    width=target_width,
                    height=target_height,
                )
                clip_path.append(clip_rect_elem)
                group.append(clip_path)

                # Apply clipping to the image
                image_kwargs["clip_path"] = f"url(#{clip_id})"

        except Exception:
            # Placeholder rectangle if image fails to load
            placeholder = dw.Rectangle(
                x=-100 / 2,
                y=-100 / 2,
                width=100,
                height=100,
                fill="gray",
                stroke="red",
                stroke_width=2,
            )
            group.append(placeholder)
            return group  # Skip image rendering on error

        # Apply stroke if specified
        if state.stroke_color and state.stroke_width > 0:
            stroke_color = state.stroke_color.to_rgb_string()
            image_kwargs["stroke"] = stroke_color
            image_kwargs["stroke_width"] = state.stroke_width

        # Create the image element
        image = dw.Image(**image_kwargs)
        group.append(image)

        return group
