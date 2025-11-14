# ============================================================================
# vood/magic/interpolation/color.py
# ============================================================================
"""Perceptual color interpolation in multiple color spaces"""

import colorsys
from enum import Enum
from typing import Tuple

from vood.core.color import Color


class ColorSpace(Enum):
    """Color space options for interpolation"""

    RGB = "rgb"  # Fast but can look muddy
    HSV = "hsv"  # Good for hue shifts and rainbow effects
    LAB = "lab"  # Most perceptually uniform (recommended)
    LCH = "lch"  # LAB in cylindrical coords (smooth hue transitions)


def color_interpolation(
    start: Color,
    end: Color,
    t: float,
    space: ColorSpace = ColorSpace.LAB,
) -> Color:
    """Interpolate between two RGB colors in specified color space

    Args:
        start: Starting RGB color (0-255, 0-255, 0-255)
        end: Ending RGB color (0-255, 0-255, 0-255)
        t: Interpolation factor (0.0 to 1.0)
        space: Color space to use for interpolation

    Returns:
        Interpolated RGB color

    Examples:
        >>> # Smooth perceptual blend (default)
        >>> interpolate_color((255, 0, 0), (0, 0, 255), 0.5)

        >>> # Rainbow effect
        >>> interpolate_color((255, 0, 0), (0, 0, 255), 0.5, ColorSpace.HSV)

        >>> # Fast for performance
        >>> interpolate_color((255, 0, 0), (0, 0, 255), 0.5, ColorSpace.RGB)
    """
    if space == ColorSpace.RGB:
        return _interpolate_rgb(start, end, t)
    elif space == ColorSpace.HSV:
        return _interpolate_hsv(start, end, t)
    elif space == ColorSpace.LAB:
        return _interpolate_lab(start, end, t)
    elif space == ColorSpace.LCH:
        return _interpolate_lch(start, end, t)

    return _interpolate_rgb(start, end, t)


# ============================================================================
# RGB Interpolation (Fast but muddy)
# ============================================================================


def _interpolate_rgb(start: Color, end: Color, t: float) -> Color:
    """Linear RGB interpolation - fast but can look muddy"""
    r = int(start[0] + (end[0] - start[0]) * t)
    g = int(start[1] + (end[1] - start[1]) * t)
    b = int(start[2] + (end[2] - start[2]) * t)
    return (r, g, b)


# ============================================================================
# HSV Interpolation (Good for hue transitions)
# ============================================================================


def _interpolate_hsv(start: Color, end: Color, t: float) -> Color:
    """HSV interpolation - good for rainbow/spectrum effects"""
    start_hsv = _rgb_to_hsv(start)
    end_hsv = _rgb_to_hsv(end)

    # Handle hue wraparound (take shortest path around color wheel)
    h_start, h_end = start_hsv[0], end_hsv[0]
    if abs(h_end - h_start) > 180:
        if h_end > h_start:
            h_start += 360
        else:
            h_end += 360

    h = (h_start + (h_end - h_start) * t) % 360
    s = start_hsv[1] + (end_hsv[1] - start_hsv[1]) * t
    v = start_hsv[2] + (end_hsv[2] - start_hsv[2]) * t

    return _hsv_to_rgb((h, s, v))


def _rgb_to_hsv(rgb: Color) -> Tuple[float, float, float]:
    """Convert RGB (0-255) to HSV (0-360, 0-100, 0-100)"""
    r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (h * 360, s * 100, v * 100)


def _hsv_to_rgb(hsv: Tuple[float, float, float]) -> Color:
    """Convert HSV (0-360, 0-100, 0-100) to RGB (0-255)"""
    h, s, v = hsv[0] / 360, hsv[1] / 100, hsv[2] / 100
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (
        max(0, min(255, int(r * 255))),
        max(0, min(255, int(g * 255))),
        max(0, min(255, int(b * 255))),
    )


# ============================================================================
# LAB Interpolation (Perceptually uniform - recommended)
# ============================================================================


def _interpolate_lab(start: Color, end: Color, t: float) -> Color:
    """LAB interpolation - most perceptually uniform"""
    start_lab = _rgb_to_lab(start)
    end_lab = _rgb_to_lab(end)

    L = start_lab[0] + (end_lab[0] - start_lab[0]) * t
    A = start_lab[1] + (end_lab[1] - start_lab[1]) * t
    B = start_lab[2] + (end_lab[2] - start_lab[2]) * t

    return _lab_to_rgb((L, A, B))


def _rgb_to_lab(rgb: Color) -> Tuple[float, float, float]:
    """Convert RGB (0-255) to LAB color space"""
    # Normalize RGB to [0, 1]
    r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255

    # Apply sRGB gamma correction
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92

    # Convert RGB to XYZ (D65 illuminant)
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    # Normalize for D65 white point
    x = x / 0.95047
    y = y / 1.00000
    z = z / 1.08883

    # Apply LAB transformation
    x = x ** (1 / 3) if x > 0.008856 else (7.787 * x) + (16 / 116)
    y = y ** (1 / 3) if y > 0.008856 else (7.787 * y) + (16 / 116)
    z = z ** (1 / 3) if z > 0.008856 else (7.787 * z) + (16 / 116)

    L = (116 * y) - 16
    A = 500 * (x - y)
    B = 200 * (y - z)

    return (L, A, B)


def _lab_to_rgb(lab: Tuple[float, float, float]) -> Color:
    """Convert LAB to RGB (0-255)"""
    L, A, B = lab

    # Convert LAB to XYZ
    y = (L + 16) / 116
    x = A / 500 + y
    z = y - B / 200

    x = 0.95047 * (x**3 if x**3 > 0.008856 else (x - 16 / 116) / 7.787)
    y = 1.00000 * (y**3 if y**3 > 0.008856 else (y - 16 / 116) / 7.787)
    z = 1.08883 * (z**3 if z**3 > 0.008856 else (z - 16 / 116) / 7.787)

    # Convert XYZ to RGB
    r = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
    g = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
    b = x * 0.0556434 + y * -0.2040259 + z * 1.0572252

    # Apply sRGB gamma correction
    r = 1.055 * (r ** (1 / 2.4)) - 0.055 if r > 0.0031308 else 12.92 * r
    g = 1.055 * (g ** (1 / 2.4)) - 0.055 if g > 0.0031308 else 12.92 * g
    b = 1.055 * (b ** (1 / 2.4)) - 0.055 if b > 0.0031308 else 12.92 * b

    # Clamp and convert to 8-bit
    r = max(0, min(255, int(r * 255 + 0.5)))
    g = max(0, min(255, int(g * 255 + 0.5)))
    b = max(0, min(255, int(b * 255 + 0.5)))

    return (r, g, b)


# ============================================================================
# LCH Interpolation (LAB in cylindrical coordinates)
# ============================================================================


def _interpolate_lch(start: Color, end: Color, t: float) -> Color:
    """LCH interpolation - LAB with smooth hue transitions"""
    start_lch = _rgb_to_lch(start)
    end_lch = _rgb_to_lch(end)

    L = start_lch[0] + (end_lch[0] - start_lch[0]) * t
    C = start_lch[1] + (end_lch[1] - start_lch[1]) * t

    # Handle hue wraparound (shortest path)
    h_start, h_end = start_lch[2], end_lch[2]
    if abs(h_end - h_start) > 180:
        if h_end > h_start:
            h_start += 360
        else:
            h_end += 360

    H = (h_start + (h_end - h_start) * t) % 360

    return _lch_to_rgb((L, C, H))


def _rgb_to_lch(rgb: Color) -> Tuple[float, float, float]:
    """Convert RGB to LCH (Lightness, Chroma, Hue)"""
    L, A, B = _rgb_to_lab(rgb)

    import math

    C = math.sqrt(A * A + B * B)
    H = math.atan2(B, A) * 180 / math.pi
    if H < 0:
        H += 360

    return (L, C, H)


def _lch_to_rgb(lch: Tuple[float, float, float]) -> Color:
    """Convert LCH to RGB"""
    import math

    L, C, H = lch

    H_rad = H * math.pi / 180
    A = C * math.cos(H_rad)
    B = C * math.sin(H_rad)

    return _lab_to_rgb((L, A, B))
