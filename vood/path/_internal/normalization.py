# ============================================================================
# vood/paths/normalization.py
# ============================================================================
"""
Complete path normalization system for morphing

Integrates robust subdivision with smart path analysis.
"""

from typing import Tuple
from vood.path.svg_path import SVGPath
from vood.path.subdivision import analyze_path_curves, subdivide_path_to_count


def equalize_curve_counts(path1: SVGPath, path2: SVGPath) -> Tuple[SVGPath, SVGPath]:
    """Equalize the number of curves in two paths through smart subdivision

    Strategy:
    1. Analyze both paths to count curves
    2. Subdivide curves in shorter path to match longer path
    3. Subdivide longest curves first for even distribution

    Args:
        path1: First path
        path2: Second path

    Returns:
        Tuple of (equalized_path1, equalized_path2) with same curve counts

    Example:
        >>> from vood.paths import line, circle_as_beziers
        >>>
        >>> path1 = line(0, 0, 100, 0)           # 1 curve
        >>> path2 = circle_as_beziers(50, 50, 30)  # 4 curves
        >>>
        >>> eq1, eq2 = equalize_curve_counts(path1, path2)
        >>> # path1 now has 4 curves too (subdivided)
    """
    # Analyze both paths
    curves1 = analyze_path_curves(path1.commands)
    curves2 = analyze_path_curves(path2.commands)

    count1 = len(curves1)
    count2 = len(curves2)

    if count1 == count2:
        return path1, path2

    # Determine which needs subdivision
    if count1 < count2:
        # Subdivide path1 to match path2
        new_commands1 = subdivide_path_to_count(path1.commands, count2)
        result1 = SVGPath(new_commands1)
        return result1, path2
    else:
        # Subdivide path2 to match path1
        new_commands2 = subdivide_path_to_count(path2.commands, count1)
        result2 = SVGPath(new_commands2)
        return path1, result2


def normalize_path_structure(path: SVGPath) -> SVGPath:
    """Normalize path structure for consistent morphing

    Ensures all paths have the same basic structure:
    - Always starts with MoveTo
    - Only contains drawing commands (no ClosePath)
    - All curves converted to cubic Beziers

    Args:
        path: Path to normalize

    Returns:
        Structurally normalized path
    """
    from ..commands import MoveTo, LineTo, CubicBezier, ClosePath

    # Convert to absolute and cubic first
    normalized = path.to_absolute().to_cubic_beziers()

    # Remove ClosePath commands - we'll handle closed paths by duplicating the start point
    new_commands = []
    start_pos = None

    for cmd in normalized.commands:
        if isinstance(cmd, MoveTo):
            new_commands.append(cmd)
            start_pos = (cmd.x, cmd.y)
        elif isinstance(cmd, ClosePath):
            # Instead of ClosePath, add a line back to start
            if start_pos is not None:
                # Convert to cubic Bezier line
                current_pos = (
                    new_commands[-1].get_end_point((0, 0)) if new_commands else (0, 0)
                )
                x1, y1 = current_pos
                x2, y2 = start_pos

                # Control points at 1/3 and 2/3 along the line
                cx1 = x1 + (x2 - x1) / 3
                cy1 = y1 + (y2 - y1) / 3
                cx2 = x1 + 2 * (x2 - x1) / 3
                cy2 = y1 + 2 * (y2 - y1) / 3

                new_commands.append(CubicBezier(cx1, cy1, cx2, cy2, x2, y2))
        else:
            new_commands.append(cmd)

    return SVGPath(new_commands)


def smart_normalize(
    path1: SVGPath, path2: SVGPath, force_cubic: bool = True
) -> Tuple[SVGPath, SVGPath]:
    """Complete normalization for morphing any two paths

    Full pipeline:
    1. Convert to absolute coordinates
    2. (Optional) Convert all to cubic Bezier curves
    3. Normalize path structures (handle ClosePath differences)
    4. Equalize curve counts through smart subdivision
    5. Verify compatibility

    Args:
        path1: First path (any structure)
        path2: Second path (any structure)
        force_cubic: If True, convert all to cubic Beziers first

    Returns:
        Tuple of fully normalized paths ready for morphing

    Raises:
        ValueError: If normalization fails

    Example:
        >>> from vood.paths import line, quadratic_curve, circle_as_beziers
        >>>
        >>> # Completely different paths!
        >>> path1 = line(0, 0, 200, 0)              # 1 straight line
        >>> path2 = circle_as_beziers(100, 0, 50)   # 4 cubic curves (closed)
        >>>
        >>> # Smart normalize makes them compatible
        >>> norm1, norm2 = smart_normalize(path1, path2)
        >>> # Both now have same structure and curve count
        >>>
        >>> # Ready to morph!
        >>> morphed = SVGPath.interpolate(norm1, norm2, t=0.5)
    """
    # Step 1: Normalize structures first
    struct1 = normalize_path_structure(path1)
    struct2 = normalize_path_structure(path2)

    # Step 2: Equalize curve counts
    try:
        eq1, eq2 = equalize_curve_counts(struct1, struct2)
    except Exception as e:
        raise ValueError(f"Failed to equalize curve counts: {e}")

    # Step 3: Verify compatibility by checking command structure
    if len(eq1.commands) != len(eq2.commands):
        # Analyze what went wrong
        curves1 = analyze_path_curves(eq1.commands)
        curves2 = analyze_path_curves(eq2.commands)
        raise ValueError(
            f"Normalization failed: different command counts after equalization. "
            f"Path 1: {len(eq1.commands)} commands ({len(curves1)} curves), "
            f"Path 2: {len(eq2.commands)} commands ({len(curves2)} curves). "
            f"The paths may have different MoveTo/ClosePath structures."
        )

    # Check if command types match
    for i, (cmd1, cmd2) in enumerate(zip(eq1.commands, eq2.commands)):
        if type(cmd1) != type(cmd2):
            raise ValueError(
                f"Normalization failed: command type mismatch at index {i}. "
                f"Path 1 has {type(cmd1).__name__}, "
                f"Path 2 has {type(cmd2).__name__}. "
                f"Paths may have incompatible structures."
            )

    return eq1, eq2


def normalize_paths_for_morphing(
    path1: SVGPath, path2: SVGPath
) -> Tuple[SVGPath, SVGPath]:
    """Normalize two paths for optimal morphing compatibility

    This is an alias for smart_normalize for backward compatibility.

    Args:
        path1: First path to normalize
        path2: Second path to normalize

    Returns:
        Tuple of (normalized_path1, normalized_path2) ready for morphing
    """
    return smart_normalize(path1, path2)
