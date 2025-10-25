from typing import Tuple, Optional, Union
import os
from PIL import Image, ImageStat


def to_rgb_string(color_str):
    """Convert various color formats to RGB string for drawsvg."""

    # Already in rgb format
    if isinstance(color_str, str) and color_str.startswith("rgb"):
        return color_str

    # Tuple format: (r, g, b)
    if isinstance(color_str, tuple) and len(color_str) == 3:
        return f"rgb({color_str[0]},{color_str[1]},{color_str[2]})"

    # String format
    if isinstance(color_str, str):
        # Remove '#' if present
        hex_str = color_str.lstrip("#")

        # Check if it's a valid 6-character hex color
        if len(hex_str) == 6 and all(c in "0123456789abcdefABCDEF" for c in hex_str):
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return f"rgb({r},{g},{b})"

        # Return as-is for named colors or other formats
        return color_str

    # Fallback
    return str(color_str)


def color_to_hex(color: Tuple[int, int, int]) -> str:
    """Convert RGB color tuple to hex string

    Args:
        color: RGB color tuple

    Returns:
        Hex color string (e.g., "#FF0000")
    """
    return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"


def get_average_color(
    filename: str, crop_percent: float, as_hex_string: bool = False
) -> Optional[Union[str, Tuple[int, int, int]]]:
    """Get the average color of an image after cropping to a specified percentage

    This function crops the image to the center crop_percent of its area, then calculates
    the average color of the remaining pixels.

    Args:
        filename: Path to the image file
        crop_percent: Percentage of the image to keep (0-100).
                     E.g., 80 keeps the center 80% and removes 10% from each edge
        as_hex_string: If True, returns hex string (e.g., "FF0000"),
                      if False returns RGB tuple (e.g., (255, 0, 0))

    Returns:
        Average color as hex string or RGB tuple, or None if error occurs
    """
    try:
        # Check if file exists
        if not os.path.exists(filename):
            return None

        # Open image with PIL
        with Image.open(filename) as image:
            # Convert to RGB if necessary (handles RGBA, etc.)
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Get image dimensions
            width, height = image.size

            # Calculate crop parameters
            start_percent = (1 - crop_percent / 100) / 2

            crop_width = round(crop_percent * width / 100)
            crop_height = round(crop_percent * height / 100)
            x = round(width * start_percent)
            y = round(height * start_percent)

            # Ensure crop dimensions are valid
            if crop_width <= 0 or crop_height <= 0:
                return None
            if x + crop_width > width or y + crop_height > height:
                return None

            # Crop the image
            cropped = image.crop((x, y, x + crop_width, y + crop_height))

            # Calculate average color using ImageStat
            stat = ImageStat.Stat(cropped)
            avg_color = [int(c) for c in stat.mean]

            # Return as requested format
            if as_hex_string:
                return f"{avg_color[0]:02X}{avg_color[1]:02X}{avg_color[2]:02X}"
            else:
                return tuple(avg_color)

    except Exception as e:
        # Handle any PIL errors, file errors, etc.
        return None
