from typing import List, Tuple
from math import cos, sin, sqrt, acos, radians, pi, hypot, tan, ceil
from .commands import CubicBezier, PathCommand  # Import needed command

# Based on principles from SVG specifications and various open-source path libraries

def arc_to_beziers(
    x1: float,
    y1: float,
    rx: float,
    ry: float,
    x_axis_rotation: float,
    large_arc_flag: int,
    sweep_flag: int,
    x2: float,
    y2: float,
) -> List[CubicBezier]:
    """
    Converts a single SVG Elliptical Arc (A) command into a list of CubicBezier commands.

    Returns:
        A list of CubicBezier objects.
    """

    try:
        # Get center, radii, and angles
        cx, cy, rx, ry, start_angle, delta_angle, rot_rad = _get_center_and_angles(
            x1, y1, x2, y2, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag
        )
    except Exception:
        # If the arc is degenerate or calculation fails, treat as a LineTo
        # Since this function must return Beziers, we convert the line to a bezier
        return [
            CubicBezier(
                x1 + (x2 - x1) / 3,
                y1 + (y2 - y1) / 3,
                x1 + 2 * (x2 - x1) / 3,
                y1 + 2 * (y2 - y1) / 3,
                x2,
                y2,
                absolute=True,
            )
        ]

    # --- Step 1: Divide the arc into segments (max 90 degrees each) ---
    num_segments = int(ceil(abs(delta_angle / (pi / 2))))
    segments = []

    # Constant used for 90-degree Bezier approximation
    # k = 4/3 * tan(angle/4)
    if num_segments == 0:
        return []

    delta_segment = delta_angle / num_segments
    k = 4.0 / 3.0 * tan(delta_segment / 4.0)

    for i in range(num_segments):
        t1 = start_angle + i * delta_segment
        t2 = t1 + delta_segment

        # Start point P0 is (x, y) at t1
        # End point P3 is (x, y) at t2

        # --- Step 2: Calculate 4 points (P0, P1, P2, P3) for the segment in Ellipse's local system ---

        # Ellipse points in rotated space (before translation)
        ex1 = rx * cos(t1)
        ey1 = ry * sin(t1)
        ex2 = rx * cos(t2)
        ey2 = ry * sin(t2)

        # Tangent vectors in rotated space (normalized)
        tan_x1 = -rx * sin(t1)
        tan_y1 = ry * cos(t1)
        tan_x2 = rx * sin(t2)  # Reversed sign due to rotation
        tan_y2 = -ry * cos(t2)  # Reversed sign due to rotation

        # Control points P1 and P2 in rotated space
        ecx1 = ex1 + k * tan_x1
        ecy1 = ey1 + k * tan_y1
        ecx2 = ex2 + k * tan_x2
        ecy2 = ey2 + k * tan_y2

        # --- Step 3: Rotate and Translate points back to original coordinate system ---

        # Rotate and translate Start Point (P0)
        px1 = cos(rot_rad) * ex1 - sin(rot_rad) * ey1 + cx
        py1 = sin(rot_rad) * ex1 + cos(rot_rad) * ey1 + cy

        # Rotate and translate Control Point 1 (P1)
        pcx1 = cos(rot_rad) * ecx1 - sin(rot_rad) * ecy1 + cx
        pcy1 = sin(rot_rad) * ecx1 + cos(rot_rad) * ecy1 + cy

        # Rotate and translate Control Point 2 (P2)
        pcx2 = cos(rot_rad) * ecx2 - sin(rot_rad) * ecy2 + cx
        pcy2 = sin(rot_rad) * ecx2 + cos(rot_rad) * ecy2 + cy

        # Rotate and translate End Point (P3)
        px2 = cos(rot_rad) * ex2 - sin(rot_rad) * ey2 + cx
        py2 = sin(rot_rad) * ex2 + cos(rot_rad) * ey2 + cy

        # The start point of the first segment should match the command's start point (x1, y1)
        # The end point of the last segment should match the command's end point (x2, y2)

        # For intermediate segments, the previous end point is the current start point
        if i == 0:
            start_x, start_y = x1, y1
        else:
            prev_end = segments[-1].get_end_point((0, 0))  # Absolute coordinates
            start_x, start_y = prev_end

        # Use the calculated end point (px2, py2) for the segment, but for the last segment
        # enforce the final (x2, y2) point to avoid floating point drift.
        end_x, end_y = (x2, y2) if i == num_segments - 1 else (px2, py2)

        # Create the CubicBezier command for this segment
        segments.append(
            CubicBezier(
                cx1=pcx1, cy1=pcy1, cx2=pcx2, cy2=pcy2, x=end_x, y=end_y, absolute=True
            )
        )

    return segments


def _vec_angle(ux: float, uy: float, vx: float, vy: float) -> float:
    """Calculate the angle between two vectors."""
    dot = ux * vx + uy * vy
    len_uv = hypot(ux, uy) * hypot(vx, vy)

    if len_uv == 0:
        return 0.0

    angle = acos(max(-1.0, min(1.0, dot / len_uv)))

    if (ux * vy - uy * vx) < 0:
        angle = -angle

    return angle


def _get_center_and_angles(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    rx: float,
    ry: float,
    x_axis_rotation: float,
    large_arc_flag: int,
    sweep_flag: int,
) -> Tuple[float, float, float, float, float]:
    """Calculates the center (cx, cy) and start/end angles (theta1, theta2) of the arc."""

    # 1. Ensure rx, ry are non-negative
    rx = abs(rx)
    ry = abs(ry)

    # 2. Convert x_axis_rotation to radians
    x_axis_rotation_rad = radians(x_axis_rotation)
    cos_rot = cos(x_axis_rotation_rad)
    sin_rot = sin(x_axis_rotation_rad)

    # 3. Transform (x1, y1) and (x2, y2) into the coordinate system rotated by x_axis_rotation
    dx = (x1 - x2) / 2
    dy = (y1 - y2) / 2

    x1_prime = cos_rot * dx + sin_rot * dy
    y1_prime = -sin_rot * dx + cos_rot * dy

    # 4. Check for degenerate case (endpoints coincide)
    if x1 == x2 and y1 == y2:
        return (
            x1,
            y1,
            x2,
            y2,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        )  # Return start/end points as center/angles are undefined

    # 5. Correct for too small radii (scale up rx, ry if necessary)
    lambda_sq = (x1_prime**2 / rx**2) + (y1_prime**2 / ry**2)
    if lambda_sq > 1:
        s = sqrt(lambda_sq)
        rx *= s
        ry *= s

    rx_sq = rx**2
    ry_sq = ry**2

    # 6. Calculate (cx_prime, cy_prime)
    # The sign of the numerator depends on the large_arc_flag and sweep_flag
    numerator = rx_sq * ry_sq - rx_sq * y1_prime**2 - ry_sq * x1_prime**2

    # Clamp to zero if negative due to floating point math
    if numerator < 0:
        numerator = 0.0

    sqrt_val = sqrt(numerator / (rx_sq * y1_prime**2 + ry_sq * x1_prime**2))

    if large_arc_flag == sweep_flag:
        sqrt_val = -sqrt_val

    cx_prime = sqrt_val * rx * y1_prime / ry
    cy_prime = -sqrt_val * ry * x1_prime / rx

    # 7. Transform (cx_prime, cy_prime) back to original coordinate system
    cx = cos_rot * cx_prime - sin_rot * cy_prime + (x1 + x2) / 2
    cy = sin_rot * cx_prime + cos_rot * cy_prime + (y1 + y2) / 2

    # 8. Calculate start angle (theta1) and end angle (theta2)

    # Vector 1: (x1' - cx', y1' - cy')
    theta1 = _vec_angle(
        1.0, 0.0, (x1_prime - cx_prime) / rx, (y1_prime - cy_prime) / ry
    )

    # Vector 2: (-x1' - cx', -y1' - cy') -> (x2' - cx', y2' - cy') is equivalent
    theta2 = _vec_angle(
        1.0, 0.0, (-x1_prime - cx_prime) / rx, (-y1_prime - cy_prime) / ry
    )

    # Adjust delta_theta to be between 0 and 2*pi
    delta_theta = theta2 - theta1

    if sweep_flag == 0 and delta_theta > 0:
        delta_theta -= 2 * pi
    elif sweep_flag == 1 and delta_theta < 0:
        delta_theta += 2 * pi

    return cx, cy, rx, ry, theta1, delta_theta, x_axis_rotation_rad
