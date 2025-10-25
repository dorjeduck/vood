import math
from typing import Tuple, Union
from typing_extensions import TypeAlias

Number: TypeAlias = Union[int, float]
Color: TypeAlias = Tuple[int, int, int]


class Interpolation:
    """Handles different types of value interpolation between two values"""

    @staticmethod
    def lerp(start: Number, end: Number, t: float) -> Number:
        """Linear interpolation between start and end values"""
        return start + (end - start) * t

    @staticmethod
    def angle(start: float, end: float, t: float) -> float:
        """Interpolate between angles in degrees, taking the shortest path"""
        # Normalize angles to 0-360 range
        start = start % 360
        end = end % 360

        # Find the shortest direction
        diff = end - start
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        return start + diff * t

    @staticmethod
    def color(start: Color, end: Color, t: float) -> Color:
        """Interpolate between RGB colors"""
        r = int(Interpolation.lerp(start[0], end[0], t))
        g = int(Interpolation.lerp(start[1], end[1], t))
        b = int(Interpolation.lerp(start[2], end[2], t))
        return (r, g, b)

    @staticmethod
    def circular_midpoint(a1, a2):
        # Convert degrees to radians
        a1_rad = math.radians(a1)
        a2_rad = math.radians(a2)

        # Convert to unit vectors
        x1, y1 = math.cos(a1_rad), math.sin(a1_rad)
        x2, y2 = math.cos(a2_rad), math.sin(a2_rad)

        # Average the vectors
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2

        # Compute the angle of the average vector
        mid_rad = math.atan2(ym, xm)
        mid_deg = math.degrees(mid_rad) % 360

        return mid_deg

    @staticmethod
    def inbetween(start, end, num):
        step = (end - start) / (num + 1)
        return [start + step * (i + 1) for i in range(num)]
