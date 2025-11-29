from typing import Optional


def angle(start: Optional[float], end: Optional[float], t: float) -> float:
    """Interpolate between angles in degrees, taking the shortest path.

    This function handles angle wraparound to ensure smooth rotation along
    the shortest arc. For example, interpolating from 350° to 10° will
    go through 0° rather than backwards through 180°.

    Args:
        start: Starting angle in degrees (None is treated as 0.0)
        end: Ending angle in degrees (None is treated as 0.0)
        t: Interpolation parameter (0.0 to 1.0)
           - t=0.0 returns start angle
           - t=1.0 returns end angle
           - t=0.5 returns midpoint along shortest path

    Returns:
        Interpolated angle in degrees

    Examples:
        >>> angle(0, 90, 0.5)
        45.0
        >>> angle(350, 10, 0.5)  # Goes through 0°, not 180°
        0.0
        >>> angle(None, 180, 1.0)  # None treated as 0
        180.0
    """
    # Handle None values - treat as 0 degrees
    if start is None:
        start = 0.0
    if end is None:
        end = 0.0

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
