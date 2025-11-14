# ============================================================================
# vood/core/color.py
# ============================================================================
"""Immutable Color class with format conversions"""

from typing import Tuple, Union
from dataclasses import dataclass

ColorTuple = Tuple[int, int, int]
ColorInput = Union["Color", ColorTuple, str]  # Accepts Color, tuple, hex, or name


@dataclass(frozen=True)
class Color:
    """Immutable RGB color with conversion utilities

    Examples:
        >>> # Create from tuple
        >>> red = Color(255, 0, 0)
        >>> red = Color.from_tuple((255, 0, 0))

        >>> # Create from hex
        >>> blue = Color.from_hex("#0000FF")
        >>> blue = Color.from_hex("0000FF")

        >>> # Create from name
        >>> green = Color.from_name("green")

        >>> # Convert formats
        >>> red.to_tuple()  # (255, 0, 0)
        >>> red.to_hex()    # "#FF0000"
        >>> red.to_rgb_string()  # "rgb(255,0,0)"

        >>> # Interpolate
        >>> purple = red.interpolate(blue, 0.5)
    """

    r: int
    g: int
    b: int

    def __post_init__(self):
        """Validate RGB values"""
        if not (0 <= self.r <= 255 and 0 <= self.g <= 255 and 0 <= self.b <= 255):
            raise ValueError(
                f"RGB values must be 0-255, got ({self.r}, {self.g}, {self.b})"
            )

    # ========================================================================
    # Creation methods
    # ========================================================================

    @classmethod
    def from_tuple(cls, rgb: Tuple[int, int, int]) -> "Color":
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
    def from_any(cls, value: Union["Color", Tuple[int, int, int], str]) -> "Color":
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

    def to_tuple(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple for rendering"""
        return (self.r, self.g, self.b)

    def to_hex(self) -> str:
        """Convert to hex string (#RRGGBB)"""
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_rgb_string(self) -> str:
        """Convert to CSS rgb() string for drawsvg

        Returns:
            String like "rgb(255,0,0)"
        """
        return f"rgb({self.r},{self.g},{self.b})"

    # ========================================================================
    # Color operations
    # ========================================================================

    def interpolate(self, other: "Color", t: float, space=None) -> "Color":
        """Interpolate to another color

        Args:
            other: Target color
            t: Interpolation factor (0.0 to 1.0)
            space: ColorSpace enum (defaults to LAB)

        Returns:
            New interpolated color
        """
        from vood.transitions.interpolation import color_interpolation, ColorSpace

        space = space or ColorSpace.LAB
        rgb = color_interpolation(self.to_tuple(), other.to_tuple(), t, space)
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
        return f"Color(r={self.r}, g={self.g}, b={self.b})"



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
