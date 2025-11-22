def angle(start: float, end: float, t: float) -> float:
    """Interpolate between angles in degrees, taking the shortest path"""
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
