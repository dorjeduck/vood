# ============================================================================
# vood/core/color.py
# ============================================================================
"""Immutable Color class with RGBA support, format conversions and interpolation"""

import colorsys
import math
from typing import Tuple, Union, Optional, Any
from enum import StrEnum

# Type aliases
ColorTuple = Tuple[int, int, int]
ColorInput = Union["Color", ColorTuple, str]


class ColorSpace(StrEnum):
    """Color space options for interpolation"""

    RGB = "rgb"  # Fast but can look muddy
    HSV = "hsv"  # Good for hue shifts and rainbow effects
    LAB = "lab"  # Most perceptually uniform (recommended)
    LCH = "lch"  # LAB in cylindrical coords (smooth hue transitions)


class Color:
    """Immutable RGBA color with conversion utilities and interpolation

    Use Color.NONE as a sentinel for "no color" (transparent/none).

    Initialization can now take any supported format directly:
    Examples:
        >>> red = Color(255, 0, 0)
        >>> blue_hex = Color("#0000FF")
        >>> blue_short = Color("#00F")  # 3-char hex codes supported
        >>> white = Color("#FFF")       # Expanded to #FFFFFF
        >>> green_name = Color("green")
        >>> existing_color = Color(blue_hex)  # Returns copy
    """

    # Define slots to make the class immutable and memory-efficient
    __slots__ = ["r", "g", "b", "a", "_is_none_sentinel", "_hash"]

    def __init__(self, *args, **kwargs):
        """Flexible initializer to create Color from various formats."""

        # Internal sentinel creation (used only by Color.NONE constant)
        if kwargs.get("_is_none_sentinel"):
            self.r = 0
            self.g = 0
            self.b = 0
            self._is_none_sentinel = True
            self._hash = hash((0, 0, 0, True))
            return

        result_r, result_g, result_b = 0, 0, 0
        result_a = 255  # Default fully opaque
        input_value = None

        if len(args) == 3 and all(isinstance(a, int) for a in args):
            # Case 1b: Color(r, g, b)
            result_r, result_g, result_b = args
        elif len(args) == 1:
            input_value = args[0]

            if isinstance(input_value, Color):
                # Case 2: Color(existing_color)
                self.__dict__.update(input_value.__dict__)
                return

            elif isinstance(input_value, tuple):
                # Case 3: Color((r, g, b)) or Color((r, g, b, a))
                if len(input_value) == 3:
                    if not all(isinstance(v, int) for v in input_value):
                        raise ValueError(
                            f"Tuple must contain integers, got {input_value}"
                        )
                    result_r, result_g, result_b = input_value

                else:
                    raise ValueError(
                        f"Tuple must contain 3  integers (r, g, b), got {input_value}"
                    )

            elif isinstance(input_value, str):
                # Case 4: Color("#hex") or Color("name")
                try:
                    r, g, b = self._parse_hex(input_value)
                    result_r, result_g, result_b = r, g, b
                except ValueError:
                    try:
                        r, g, b = self._parse_name(input_value)
                        result_r, result_g, result_b = r, g, b
                    except ValueError:
                        raise ValueError(
                            f"Cannot convert string '{input_value}' to Color (not hex or known name)."
                        )
            else:
                raise ValueError(f"Cannot initialize Color from {type(input_value)}")
        else:
            raise ValueError(
                "Color must be initialized with Color(r, g, b[, a]), Color(hex_str), Color(name), or Color(tuple)."
            )

        # --- Final Assignment and Validation ---
        self.r = result_r
        self.g = result_g
        self.b = result_b

        self._is_none_sentinel = False

        if not (0 <= self.r <= 255 and 0 <= self.g <= 255 and 0 <= self.b <= 255):
            raise ValueError(
                f"RGB values must be 0-255, got ({self.r}, {self.g}, {self.b})"
            )

        # Pre-calculate hash for immutability
        self._hash = hash((self.r, self.g, self.b, self._is_none_sentinel))

    def is_none(self) -> bool:
        """Check if this is the special NONE sentinel (no color)"""
        return self._is_none_sentinel

    def __eq__(self, other: Any) -> bool:
        """Equality check for comparison and set/dict use"""
        if not isinstance(other, Color):
            return NotImplemented
        return (self.r, self.g, self.b, self._is_none_sentinel) == (
            other.r,
            other.g,
            other.b,
            other._is_none_sentinel,
        )

    def __hash__(self) -> int:
        """Return pre-calculated hash (necessary for immutability)"""
        return self._hash

    # ========================================================================
    # Creation methods
    # ========================================================================

    @staticmethod
    def _parse_hex(hex_str: str) -> ColorTuple:
        """Internal helper to create from hex string

        Supports both 6-character (#RRGGBB) and 3-character (#RGB) hex codes.
        3-character codes are expanded: #FFF -> #FFFFFF, #F00 -> #FF0000
        """
        hex_str = hex_str.lstrip("#")

        # Validate characters
        if not all(c in "0123456789abcdefABCDEF" for c in hex_str):
            raise ValueError(f"Invalid hex color: {hex_str}")

        # Handle 3-character hex codes (#RGB -> #RRGGBB)
        if len(hex_str) == 3:
            hex_str = "".join([c * 2 for c in hex_str])
        elif len(hex_str) != 6:
            raise ValueError(f"Invalid hex color length: {hex_str} (must be 3 or 6 characters)")

        return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

    @staticmethod
    def _parse_name(name: str) -> ColorTuple:
        """Internal helper to create from CSS color name"""
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
        return rgb

    @classmethod
    def from_tuple(cls, rgb: ColorTuple) -> "Color":
        """Create from RGB or RGBA tuple"""
        return cls(rgb)

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Create from hex string"""
        return cls(hex_str)

    @classmethod
    def from_name(cls, name: str) -> "Color":
        """Create from CSS color name"""
        return cls(name)

    # ========================================================================
    # Conversion methods
    # ========================================================================

    def to_tuple(self) -> Optional[ColorTuple]:
        """Convert to RGB tuple (without alpha) for rendering"""
        if self.is_none():
            return None
        return (self.r, self.g, self.b)

    def to_hex(self) -> str:
        """Convert to hex string (#RRGGBB) or 'none'"""
        if self.is_none():
            return "none"
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_rgb_string(self) -> str:
        """Convert to CSS rgb() or rgba() string for drawsvg or 'none'"""
        if self.is_none():
            return "none"

        return f"rgb({self.r},{self.g},{self.b})"

    # ========================================================================
    # Color operations
    # ========================================================================

    def interpolate(
        self, other: "Color", t: float, space: ColorSpace = ColorSpace.LAB
    ) -> "Color":
        """Interpolate to another color (including alpha channel)"""
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

        return Color(rgb[0], rgb[1], rgb[2])

    def with_alpha(self, alpha: int) -> "Color":
        """Create a new color with different alpha value

        Args:
            alpha: Alpha value 0-255 (0=transparent, 255=opaque)

        Returns:
            New Color instance with updated alpha
        """
        if not (0 <= alpha <= 255):
            raise ValueError(f"Alpha must be 0-255, got {alpha}")
        return Color(self.r, self.g, self.b, alpha)

    def darken(self, amount: int) -> "Color":
        """Create darker version of this color (preserves alpha)"""
        return Color(
            max(0, self.r - amount),
            max(0, self.g - amount),
            max(0, self.b - amount),
        )

    def lighten(self, amount: int) -> "Color":
        """Create lighter version of this color (preserves alpha)"""
        return Color(
            min(255, self.r + amount),
            min(255, self.g + amount),
            min(255, self.b + amount),
        )

    def with_opacity(self, opacity: float) -> "Color":
        """Create color with opacity (0.0 to 1.0)

        Args:
            opacity: Opacity value 0.0 (transparent) to 1.0 (opaque)

        Returns:
            New Color with alpha set from opacity
        """
        return self.with_alpha(int(opacity * 255))

    # ========================================================================
    # Special methods
    # ========================================================================

    def __bool__(self) -> bool:
        """Make Color.NONE falsy, real colors truthy"""
        return not self.is_none()

    def __iter__(self):
        """Allow unpacking: r, g, b = color"""
        yield self.r
        yield self.g
        yield self.b

    def __str__(self) -> str:
        """String representation"""
        return self.to_hex()

    def __repr__(self) -> str:
        """Developer representation"""
        if self.is_none():
            return "Color.NONE"

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

# Basic colors
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

# Additional web colors
PINK = Color(255, 192, 203)
LIME = Color(0, 255, 0)
TEAL = Color(0, 128, 128)
INDIGO = Color(75, 0, 130)
VIOLET = Color(238, 130, 238)
BROWN = Color(165, 42, 42)
GRAY = Color(128, 128, 128)
SILVER = Color(192, 192, 192)
GOLD = Color(255, 215, 0)

# Material design colors
RED_500 = Color(244, 67, 54)
PINK_500 = Color(233, 30, 99)
PURPLE_500 = Color(156, 39, 176)
DEEP_PURPLE_500 = Color(103, 58, 183)
INDIGO_500 = Color(63, 81, 181)
BLUE_500 = Color(33, 150, 243)
LIGHT_BLUE_500 = Color(3, 169, 244)
CYAN_500 = Color(0, 188, 212)
TEAL_500 = Color(0, 150, 136)
GREEN_500 = Color(76, 175, 80)
LIGHT_GREEN_500 = Color(139, 195, 74)
LIME_500 = Color(205, 220, 57)
YELLOW_500 = Color(255, 235, 59)
AMBER_500 = Color(255, 193, 7)
ORANGE_500 = Color(255, 152, 0)
DEEP_ORANGE_500 = Color(255, 87, 34)
BROWN_500 = Color(121, 85, 72)
GREY_500 = Color(158, 158, 158)
BLUE_GREY_500 = Color(96, 125, 139)



# Special sentinel for "no color" (transparent/none)
# This is a singleton - use Color.NONE
Color.NONE = Color(_is_none_sentinel=True)
