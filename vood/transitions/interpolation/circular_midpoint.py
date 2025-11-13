import math


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
