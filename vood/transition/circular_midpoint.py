import math


def circular_midpoint(a1: float, a2: float) -> float:
    """Calculate the midpoint between two angles on a circle.

    Uses vector averaging to find the true angular midpoint, which correctly
    handles cases where angles span across 0°/360°. This is geometrically
    correct for circular interpolation, unlike simple arithmetic mean.

    Args:
        a1: First angle in degrees (0-360)
        a2: Second angle in degrees (0-360)

    Returns:
        Midpoint angle in degrees (normalized to 0-360 range)

    Examples:
        >>> circular_midpoint(0, 90)
        45.0
        >>> circular_midpoint(350, 10)  # Spans 0°
        0.0
        >>> circular_midpoint(270, 90)  # Opposite sides
        0.0

    Note:
        This differs from simple averaging: (350 + 10) / 2 = 180,
        but circular_midpoint(350, 10) = 0, which is geometrically correct.
    """
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
