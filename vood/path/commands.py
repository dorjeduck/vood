# ============================================================================
# vood/paths/commands.py
# ============================================================================
"""SVG Path Command Classes"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
from abc import ABC, abstractmethod
import math


@dataclass
class PathCommand(ABC):
    """Abstract base class for SVG path commands"""

    @abstractmethod
    def to_string(self) -> str:
        """Convert command to SVG path string format"""
        pass

    @abstractmethod
    def to_absolute(self, current_pos: Tuple[float, float]) -> PathCommand:
        """Convert to absolute coordinates"""
        pass

    @abstractmethod
    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Get the end point of this command"""
        pass

    @abstractmethod
    def interpolate(self, other: PathCommand, t: float) -> PathCommand:
        """Interpolate between this command and another at time t (0.0 to 1.0)"""
        pass


@dataclass
class MoveTo(PathCommand):
    """M or m command - Move to a point"""

    x: float
    y: float
    absolute: bool = True

    def to_string(self) -> str:
        cmd = "M" if self.absolute else "m"
        return f"{cmd} {self.x},{self.y}"

    def to_absolute(self, current_pos: Tuple[float, float]) -> MoveTo:
        if self.absolute:
            return self
        return MoveTo(current_pos[0] + self.x, current_pos[1] + self.y)

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        if self.absolute:
            return (self.x, self.y)
        return (current_pos[0] + self.x, current_pos[1] + self.y)

    def interpolate(self, other: PathCommand, t: float) -> MoveTo:
        if not isinstance(other, MoveTo):
            raise ValueError(f"Cannot interpolate MoveTo with {type(other).__name__}")
        return MoveTo(
            x=self.x + (other.x - self.x) * t,
            y=self.y + (other.y - self.y) * t,
            absolute=True,  # Interpolated path should use absolute
        )


@dataclass
class LineTo(PathCommand):
    """L or l command - Draw a line to a point"""

    x: float
    y: float
    absolute: bool = True

    def to_string(self) -> str:
        cmd = "L" if self.absolute else "l"
        return f"{cmd} {self.x},{self.y}"

    def to_absolute(self, current_pos: Tuple[float, float]) -> LineTo:
        if self.absolute:
            return self
        return LineTo(current_pos[0] + self.x, current_pos[1] + self.y)

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        if self.absolute:
            return (self.x, self.y)
        return (current_pos[0] + self.x, current_pos[1] + self.y)

    def interpolate(self, other: PathCommand, t: float) -> LineTo:
        if not isinstance(other, LineTo):
            raise ValueError(f"Cannot interpolate LineTo with {type(other).__name__}")
        return LineTo(
            x=self.x + (other.x - self.x) * t,
            y=self.y + (other.y - self.y) * t,
            absolute=True,
        )


# --- New Commands: Horizontal and Vertical Lines ---


@dataclass
class HorizontalLine(PathCommand):
    """H or h command - Draw a horizontal line to a new x coordinate"""

    x: float
    absolute: bool = True

    def to_string(self) -> str:
        cmd = "H" if self.absolute else "h"
        return f"{cmd} {self.x}"

    def to_absolute(self, current_pos: Tuple[float, float]) -> LineTo:
        """Converts to a standard LineTo command with the current y-coordinate"""
        if self.absolute:
            return LineTo(self.x, current_pos[1])
        return LineTo(current_pos[0] + self.x, current_pos[1])

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        if self.absolute:
            return (self.x, current_pos[1])
        return (current_pos[0] + self.x, current_pos[1])

    def interpolate(self, other: PathCommand, t: float) -> HorizontalLine:
        if not isinstance(other, HorizontalLine):
            raise ValueError(
                f"Cannot interpolate HorizontalLine with {type(other).__name__}"
            )
        return HorizontalLine(x=self.x + (other.x - self.x) * t, absolute=True)


@dataclass
class VerticalLine(PathCommand):
    """V or v command - Draw a vertical line to a new y coordinate"""

    y: float
    absolute: bool = True

    def to_string(self) -> str:
        cmd = "V" if self.absolute else "v"
        return f"{cmd} {self.y}"

    def to_absolute(self, current_pos: Tuple[float, float]) -> LineTo:
        """Converts to a standard LineTo command with the current x-coordinate"""
        if self.absolute:
            return LineTo(current_pos[0], self.y)
        return LineTo(current_pos[0], current_pos[1] + self.y)

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        if self.absolute:
            return (current_pos[0], self.y)
        return (current_pos[0], current_pos[1] + self.y)

    def interpolate(self, other: PathCommand, t: float) -> VerticalLine:
        if not isinstance(other, VerticalLine):
            raise ValueError(
                f"Cannot interpolate VerticalLine with {type(other).__name__}"
            )
        return VerticalLine(y=self.y + (other.y - self.y) * t, absolute=True)


# --- Bezier Curves ---


@dataclass
class QuadraticBezier(PathCommand):
    """Q or q command - Quadratic Bezier curve"""

    cx: float
    cy: float
    x: float
    y: float
    absolute: bool = True

    def to_string(self) -> str:
        cmd = "Q" if self.absolute else "q"
        return f"{cmd} {self.cx},{self.cy} {self.x},{self.y}"

    def to_absolute(self, current_pos: Tuple[float, float]) -> QuadraticBezier:
        if self.absolute:
            return self
        return QuadraticBezier(
            cx=current_pos[0] + self.cx,
            cy=current_pos[1] + self.cy,
            x=current_pos[0] + self.x,
            y=current_pos[1] + self.y,
            absolute=True,
        )

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        if self.absolute:
            return (self.x, self.y)
        return (current_pos[0] + self.x, current_pos[1] + self.y)

    def interpolate(self, other: PathCommand, t: float) -> QuadraticBezier:
        if not isinstance(other, QuadraticBezier):
            raise ValueError(
                f"Cannot interpolate QuadraticBezier with {type(other).__name__}"
            )
        return QuadraticBezier(
            cx=self.cx + (other.cx - self.cx) * t,
            cy=self.cy + (other.cy - self.cy) * t,
            x=self.x + (other.x - self.x) * t,
            y=self.y + (other.y - self.y) * t,
            absolute=True,
        )


@dataclass
class CubicBezier(PathCommand):
    """C or c command - Cubic Bezier curve"""

    cx1: float
    cy1: float
    cx2: float
    cy2: float
    x: float
    y: float
    absolute: bool = True

    def to_string(self) -> str:
        cmd = "C" if self.absolute else "c"
        return f"{cmd} {self.cx1},{self.cy1} {self.cx2},{self.cy2} {self.x},{self.y}"

    def to_absolute(self, current_pos: Tuple[float, float]) -> CubicBezier:
        if self.absolute:
            return self
        return CubicBezier(
            cx1=current_pos[0] + self.cx1,
            cy1=current_pos[1] + self.cy1,
            cx2=current_pos[0] + self.cx2,
            cy2=current_pos[1] + self.cy2,
            x=current_pos[0] + self.x,
            y=current_pos[1] + self.y,
            absolute=True,
        )

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        if self.absolute:
            return (self.x, self.y)
        return (current_pos[0] + self.x, current_pos[1] + self.y)

    def interpolate(self, other: PathCommand, t: float) -> CubicBezier:
        if not isinstance(other, CubicBezier):
            raise ValueError(
                f"Cannot interpolate CubicBezier with {type(other).__name__}"
            )
        return CubicBezier(
            cx1=self.cx1 + (other.cx1 - self.cx1) * t,
            cy1=self.cy1 + (other.cy1 - self.cy1) * t,
            cx2=self.cx2 + (other.cx2 - self.cx2) * t,
            cy2=self.cy2 + (other.cy2 - self.cy2) * t,
            x=self.x + (other.x - self.x) * t,
            y=self.y + (other.y - self.y) * t,
            absolute=True,
        )


# --- New Commands: Smooth Bezier Curves ---


@dataclass
class SmoothQuadraticBezier(PathCommand):
    """T or t command - Smooth Quadratic Bezier curve (T = QuadraticBezier with reflected control point)"""

    x: float
    y: float
    absolute: bool = True

    def to_string(self) -> str:
        cmd = "T" if self.absolute else "t"
        return f"{cmd} {self.x},{self.y}"

    def to_absolute(self, current_pos: Tuple[float, float]) -> SmoothQuadraticBezier:
        if self.absolute:
            return self
        return SmoothQuadraticBezier(
            x=current_pos[0] + self.x, y=current_pos[1] + self.y, absolute=True
        )

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        if self.absolute:
            return (self.x, self.y)
        return (current_pos[0] + self.x, current_pos[1] + self.y)

    def interpolate(self, other: PathCommand, t: float) -> SmoothQuadraticBezier:
        if not isinstance(other, SmoothQuadraticBezier):
            raise ValueError(
                f"Cannot interpolate SmoothQuadraticBezier with {type(other).__name__}"
            )
        return SmoothQuadraticBezier(
            x=self.x + (other.x - self.x) * t,
            y=self.y + (other.y - self.y) * t,
            absolute=True,
        )


@dataclass
class SmoothCubicBezier(PathCommand):
    """S or s command - Smooth Cubic Bezier curve (S = CubicBezier with reflected control point 1)"""

    cx2: float
    cy2: float
    x: float
    y: float
    absolute: bool = True

    def to_string(self) -> str:
        cmd = "S" if self.absolute else "s"
        return f"{cmd} {self.cx2},{self.cy2} {self.x},{self.y}"

    def to_absolute(self, current_pos: Tuple[float, float]) -> SmoothCubicBezier:
        if self.absolute:
            return self
        return SmoothCubicBezier(
            cx2=current_pos[0] + self.cx2,
            cy2=current_pos[1] + self.cy2,
            x=current_pos[0] + self.x,
            y=current_pos[1] + self.y,
            absolute=True,
        )

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        if self.absolute:
            return (self.x, self.y)
        return (current_pos[0] + self.x, current_pos[1] + self.y)

    def interpolate(self, other: PathCommand, t: float) -> SmoothCubicBezier:
        if not isinstance(other, SmoothCubicBezier):
            raise ValueError(
                f"Cannot interpolate SmoothCubicBezier with {type(other).__name__}"
            )
        return SmoothCubicBezier(
            cx2=self.cx2 + (other.cx2 - self.cx2) * t,
            cy2=self.cy2 + (other.cy2 - self.cy2) * t,
            x=self.x + (other.x - self.x) * t,
            y=self.y + (other.y - self.y) * t,
            absolute=True,
        )


# --- New Command: Arc ---


@dataclass
class Arc(PathCommand):
    """A or a command - Elliptical Arc curve"""

    rx: float
    ry: float
    x_axis_rotation: float
    large_arc_flag: int
    sweep_flag: int
    x: float
    y: float
    absolute: bool = True

    def to_string(self) -> str:
        cmd = "A" if self.absolute else "a"
        # Flags (large_arc_flag, sweep_flag) are 0 or 1 integers
        return (
            f"{cmd} {self.rx},{self.ry} {self.x_axis_rotation} "
            f"{self.large_arc_flag},{self.sweep_flag} {self.x},{self.y}"
        )

    def to_absolute(self, current_pos: Tuple[float, float]) -> Arc:
        if self.absolute:
            return self
        return Arc(
            rx=self.rx,
            ry=self.ry,
            x_axis_rotation=self.x_axis_rotation,
            large_arc_flag=self.large_arc_flag,
            sweep_flag=self.sweep_flag,
            x=current_pos[0] + self.x,
            y=current_pos[1] + self.y,
            absolute=True,
        )

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        if self.absolute:
            return (self.x, self.y)
        return (current_pos[0] + self.x, current_pos[1] + self.y)

    def interpolate(self, other: PathCommand, t: float) -> Arc:
        if not isinstance(other, Arc):
            raise ValueError(f"Cannot interpolate Arc with {type(other).__name__}")

        # Interpolate all numeric parameters. Flags (0/1) are usually kept constant
        # during simple interpolation, or one path dominates for the whole morph.
        # We will interpolate them here, and rely on rounding/clamping later if needed.
        return Arc(
            rx=self.rx + (other.rx - self.rx) * t,
            ry=self.ry + (other.ry - self.ry) * t,
            x_axis_rotation=self.x_axis_rotation
            + (other.x_axis_rotation - self.x_axis_rotation) * t,
            large_arc_flag=round(
                self.large_arc_flag + (other.large_arc_flag - self.large_arc_flag) * t
            ),
            sweep_flag=round(
                self.sweep_flag + (other.sweep_flag - self.sweep_flag) * t
            ),
            x=self.x + (other.x - self.x) * t,
            y=self.y + (other.y - self.y) * t,
            absolute=True,
        )


# --- Close Path ---


@dataclass
class ClosePath(PathCommand):
    """Z or z command - Close the path"""

    def to_string(self) -> str:
        return "Z"

    def to_absolute(self, current_pos: Tuple[float, float]) -> ClosePath:
        return self

    def get_end_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        # NOTE: In a real implementation, ClosePath needs access to the start
        # point of the current subpath (the last MoveTo). For simplicity here,
        # we return the current position, as the path consumer handles the Z command.
        return current_pos  # This is technically incorrect but sufficient for morphing

    def interpolate(self, other: PathCommand, t: float) -> ClosePath:
        if not isinstance(other, ClosePath):
            raise ValueError(
                f"Cannot interpolate ClosePath with {type(other).__name__}"
            )
        return self
