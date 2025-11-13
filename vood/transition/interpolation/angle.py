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
