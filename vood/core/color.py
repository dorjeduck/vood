# ============================================================================
# vood/core/color.py
# ============================================================================
"""Immutable Color class with format conversions and interpolation"""

import colorsys
import math
from typing import Tuple, Union, Optional
from dataclasses import dataclass
from enum import Enum

# Type aliases
ColorTuple = Tuple[int, int, int]
ColorInput = Union["Color", ColorTuple, str]  # Accepts Color, tuple, hex, or name


class ColorSpace(Enum):
    """Color space options for interpolation"""

    RGB = "rgb"  # Fast but can look muddy
    HSV = "hsv"  # Good for hue shifts and rainbow effects
    LAB = "lab"  # Most perceptually uniform (recommended)
    LCH = "lch"  # LAB in cylindrical coords (smooth hue transitions)


@dataclass(frozen=True)
class Color:
    """Immutable RGB color with conversion utilities and interpolation

    Use Color.NONE as a sentinel for "no color" (transparent/none).

    Examples:
        >>> # Create from tuple
        >>> red = Color(255, 0, 0)
        >>> red = Color.from_tuple((255, 0, 0))

        >>> # Create from hex
        >>> blue = Color.from_hex("#0000FF")
        >>> blue = Color.from_hex("0000FF")

        >>> # Create from name
        >>> green = Color.from_name("green")

        >>> # No color (transparent)
        >>> transparent = Color.NONE
        >>> transparent.to_rgb_string()  # "none"
        >>> transparent.is_none()  # True

        >>> # Convert formats
        >>> red.to_tuple()  # (255, 0, 0)
        >>> red.to_hex()    # "#FF0000"
        >>> red.to_rgb_string()  # "rgb(255,0,0)"

        >>> # Interpolate
        >>> purple = red.interpolate(blue, 0.5)
        >>> rainbow = red.interpolate(blue, 0.5, ColorSpace.HSV)
    """

    r: int
    g: int
    b: int
    _is_none_sentinel: bool = False

    def __post_init__(self):
        """Validate RGB values"""
        # Skip validation for the NONE sentinel
        if self._is_none_sentinel:
            return

        if not (0 <= self.r <= 255 and 0 <= self.g <= 255 and 0 <= self.b <= 255):
            raise ValueError(
                f"RGB values must be 0-255, got ({self.r}, {self.g}, {self.b})"
            )

    def is_none(self) -> bool:
        """Check if this is the special NONE sentinel (no color)"""
        return self._is_none_sentinel

    # ========================================================================
    # Creation methods
    # ========================================================================

    @classmethod
    def from_tuple(cls, rgb: ColorTuple) -> "Color":
        """Create from RGB tuple"""
        return cls(rgb[0], rgb[1], rgb[2])

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Create from hex string

        Args:
            hex_str: Hex string like "#FF0000" or "FF0000"
        """
        hex_str = hex_str.lstrip("#")
        if len(hex_str) != 6 or not all(c in "0123456789abcdefABCDEF" for c in hex_str):
            raise ValueError(f"Invalid hex color: {hex_str}")

        return cls(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

    @classmethod
    def from_name(cls, name: str) -> "Color":
        """Create from CSS color name"""
        colors = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "pink": (255, 192, 203),
            "brown": (165, 42, 42),
            "gray": (128, 128, 128),
            "grey": (128, 128, 128),
        }
        rgb = colors.get(name.lower())
        if not rgb:
            raise ValueError(f"Unknown color name: {name}")
        return cls.from_tuple(rgb)

    @classmethod
    def from_any(cls, value: ColorInput) -> "Color":
        """Create from any supported format

        Args:
            value: Color, tuple, hex string, or color name

        Examples:
            >>> Color.from_any((255, 0, 0))
            >>> Color.from_any("#FF0000")
            >>> Color.from_any("red")
            >>> Color.from_any(existing_color)  # Returns as-is
        """
        if isinstance(value, Color):
            return value

        if isinstance(value, tuple):
            return cls.from_tuple(value)

        if isinstance(value, str):
            # Try hex first
            if value.startswith("#") or (
                len(value) == 6 and all(c in "0123456789abcdefABCDEF" for c in value)
            ):
                return cls.from_hex(value)
            # Try name
            return cls.from_name(value)

        raise ValueError(f"Cannot convert {type(value)} to Color")

    # ========================================================================
    # Conversion methods
    # ========================================================================

    def to_tuple(self) -> Optional[ColorTuple]:
        """Convert to RGB tuple for rendering

        Returns:
            RGB tuple or None if this is Color.NONE
        """
        if self.is_none():
            return None
        return (self.r, self.g, self.b)

    def to_hex(self) -> str:
        """Convert to hex string (#RRGGBB) or 'none'"""
        if self.is_none():
            return "none"
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_rgb_string(self) -> str:
        """Convert to CSS rgb() string for drawsvg or 'none'

        Returns:
            String like "rgb(255,0,0)" or "none"
        """
        if self.is_none():
            return "none"
        return f"rgb({self.r},{self.g},{self.b})"

    # ========================================================================
    # Color operations
    # ========================================================================

    def interpolate(
        self, other: "Color", t: float, space: ColorSpace = ColorSpace.LAB
    ) -> "Color":
        """Interpolate to another color

        Args:
            other: Target color
            t: Interpolation factor (0.0 to 1.0)
            space: ColorSpace enum (defaults to LAB for perceptual uniformity)

        Returns:
            New interpolated color

        Examples:
            >>> red = Color(255, 0, 0)
            >>> blue = Color(0, 0, 255)
            >>> purple = red.interpolate(blue, 0.5)  # Perceptual blend
            >>> rainbow = red.interpolate(blue, 0.5, ColorSpace.HSV)  # Rainbow

        Note:
            If either color is Color.NONE, returns the other color (step transition)
        """
        # Handle NONE colors - step transition
        if self.is_none():
            return other
        if other.is_none():
            return self

        if space == ColorSpace.RGB:
            rgb = _interpolate_rgb(self, other, t)
        elif space == ColorSpace.HSV:
            rgb = _interpolate_hsv(self, other, t)
        elif space == ColorSpace.LAB:
            rgb = _interpolate_lab(self, other, t)
        elif space == ColorSpace.LCH:
            rgb = _interpolate_lch(self, other, t)
        else:
            rgb = _interpolate_rgb(self, other, t)

        return Color.from_tuple(rgb)

    def darken(self, amount: int) -> "Color":
        """Create darker version of this color

        Args:
            amount: Amount to darken (0-255)
        """
        return Color(
            max(0, self.r - amount), max(0, self.g - amount), max(0, self.b - amount)
        )

    def lighten(self, amount: int) -> "Color":
        """Create lighter version of this color

        Args:
            amount: Amount to lighten (0-255)
        """
        return Color(
            min(255, self.r + amount),
            min(255, self.g + amount),
            min(255, self.b + amount),
        )

    def with_opacity(self, opacity: float) -> Tuple[int, int, int, int]:
        """Return RGBA tuple with opacity

        Args:
            opacity: Opacity value (0.0 to 1.0)

        Returns:
            RGBA tuple (r, g, b, alpha)
        """
        return (self.r, self.g, self.b, int(opacity * 255))

    # ========================================================================
    # Special methods
    # ========================================================================

    def __bool__(self) -> bool:
        """Make Color.NONE falsy, real colors truthy

        Allows: if color: ...
        """
        return not self.is_none()

    def __iter__(self):
        """Allow unpacking: r, g, b = color

        Note: Color.NONE yields (0, 0, 0) but shouldn't be unpacked
        """
        yield self.r
        yield self.g
        yield self.b

    def __str__(self) -> str:
        """String representation"""
        return self.to_hex()

    def __repr__(self) -> str:
        """Developer representation"""
        return f"Color(r={self.r}, g={self.g}, b={self.b})"


# ============================================================================
# Interpolation implementation (internal functions)
# ============================================================================


def _interpolate_rgb(start: Color, end: Color, t: float) -> ColorTuple:
    """Linear RGB interpolation - fast but can look muddy"""
    r = int(start.r + (end.r - start.r) * t)
    g = int(start.g + (end.g - start.g) * t)
    b = int(start.b + (end.b - start.b) * t)
    return (r, g, b)


def _interpolate_hsv(start: Color, end: Color, t: float) -> ColorTuple:
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


def _rgb_to_hsv(color: Color) -> Tuple[float, float, float]:
    """Convert RGB (0-255) to HSV (0-360, 0-100, 0-100)"""
    r, g, b = color.r / 255, color.g / 255, color.b / 255
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (h * 360, s * 100, v * 100)


def _hsv_to_rgb(hsv: Tuple[float, float, float]) -> ColorTuple:
    """Convert HSV (0-360, 0-100, 0-100) to RGB (0-255)"""
    h, s, v = hsv[0] / 360, hsv[1] / 100, hsv[2] / 100
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (
        max(0, min(255, int(r * 255))),
        max(0, min(255, int(g * 255))),
        max(0, min(255, int(b * 255))),
    )


def _interpolate_lab(start: Color, end: Color, t: float) -> ColorTuple:
    """LAB interpolation - most perceptually uniform"""
    start_lab = _rgb_to_lab(start)
    end_lab = _rgb_to_lab(end)

    L = start_lab[0] + (end_lab[0] - start_lab[0]) * t
    A = start_lab[1] + (end_lab[1] - start_lab[1]) * t
    B = start_lab[2] + (end_lab[2] - start_lab[2]) * t

    return _lab_to_rgb((L, A, B))


def _rgb_to_lab(color: Color) -> Tuple[float, float, float]:
    """Convert RGB (0-255) to LAB color space"""
    # Normalize RGB to [0, 1]
    r, g, b = color.r / 255, color.g / 255, color.b / 255

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


def _lab_to_rgb(lab: Tuple[float, float, float]) -> ColorTuple:
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


def _interpolate_lch(start: Color, end: Color, t: float) -> ColorTuple:
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


def _rgb_to_lch(color: Color) -> Tuple[float, float, float]:
    """Convert RGB to LCH (Lightness, Chroma, Hue)"""
    L, A, B = _rgb_to_lab(color)

    C = math.sqrt(A * A + B * B)
    H = math.atan2(B, A) * 180 / math.pi
    if H < 0:
        H += 360

    return (L, C, H)


def _lch_to_rgb(lch: Tuple[float, float, float]) -> ColorTuple:
    """Convert LCH to RGB"""
    L, C, H = lch

    H_rad = H * math.pi / 180
    A = C * math.cos(H_rad)
    B = C * math.sin(H_rad)

    return _lab_to_rgb((L, A, B))


# ============================================================================
# Common colors as constants
# ============================================================================

RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)
YELLOW = Color(255, 255, 0)
CYAN = Color(0, 255, 255)
MAGENTA = Color(255, 0, 255)
ORANGE = Color(255, 165, 0)
PURPLE = Color(128, 0, 128)

# Special sentinel for "no color" (transparent/none)
# This is a singleton - use Color.NONE, not Color(0, 0, 0, _is_none_sentinel=True)
Color.NONE = Color(0, 0, 0, _is_none_sentinel=True)
