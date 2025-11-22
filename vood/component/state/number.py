"""State class for number digits (0-9) with monospaced font design"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

from .base import State
from .base_vertex import VertexState
from vood.component.vertex import VertexContours, VertexLoop
from vood.transition import easing
from vood.core.color import Color


@dataclass(frozen=True)
class NumberState(VertexState):
    """State class for rendering single digits 0-9 with beautiful monospaced design

    Each digit has a custom vertex representation inspired by modern digital fonts,
    designed to work seamlessly with vertex-based morphing.

    Attributes:
        digit: The digit to display (0-9)
        width: Width of the character
        height: Height of the character
    """

    digit: int = 0
    width: float = 30
    height: float = 50

    DEFAULT_EASING = {
        **State.DEFAULT_EASING,
        "digit": easing.step,
        "width": easing.in_out,
        "height": easing.in_out,
    }

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.digit, int) or self.digit < 0 or self.digit > 9:
            raise ValueError(f"digit must be an integer from 0-9, got {self.digit}")



    def _generate_contours(self) -> VertexContours:
        """Generate contours for the specified digit

        Returns VertexContours with the digit's vertex representation.
        All digits are designed in a normalized space and then scaled.
        Digits 0, 6, 8, 9 include hole contours.
        """
        # Get normalized vertices and holes for the digit (in unit space)
        normalized_outer, normalized_holes = self._get_digit_contours(self.digit)

        # Scale to desired width and height
        scaled_outer = [
            (x * self.width, y * self.height)
            for x, y in normalized_outer
        ]

        # Resample outer contour to match _num_vertices
        resampled_outer = self._resample_vertices(scaled_outer, self._num_vertices)
        outer_loop = VertexLoop(resampled_outer, closed=self.closed)

        # Process holes if present
        hole_loops = None
        if normalized_holes:
            hole_loops = []
            # Each hole gets proportional vertex count based on its length
            for hole_verts in normalized_holes:
                scaled_hole = [
                    (x * self.width, y * self.height)
                    for x, y in hole_verts
                ]
                # Use fewer vertices for holes (typically 1/3 of outer)
                hole_vertex_count = max(8, self._num_vertices // 3)
                resampled_hole = self._resample_vertices(scaled_hole, hole_vertex_count)
                hole_loops.append(VertexLoop(resampled_hole, closed=True))

        return VertexContours(outer=outer_loop, holes=hole_loops)

    def _get_digit_contours(self, digit: int) -> tuple[List[Tuple[float, float]], List[List[Tuple[float, float]]] | None]:
        """Get normalized contours (outer + holes) for a digit (centered at origin)

        All coordinates are normalized to roughly [-0.5, 0.5] range for both x and y,
        making them centered at origin and ready for scaling.

        Returns:
            Tuple of (outer_vertices, holes_vertices_list)
            holes_vertices_list is None for digits without holes, or a list of hole vertex lists
        """
        # Beautiful monospaced design for each digit
        # Using 7-segment inspired geometry with smooth rounded connections

        if digit == 0:
            # Rounded rectangle with hole in center
            outer = [
                (-0.4, -0.5), (0.4, -0.5), (0.5, -0.4), (0.5, 0.4),
                (0.4, 0.5), (-0.4, 0.5), (-0.5, 0.4), (-0.5, -0.4)
            ]
            # Inner hole (smaller rounded rectangle)
            hole = [
                (-0.25, -0.35), (0.25, -0.35), (0.3, -0.3), (0.3, 0.3),
                (0.25, 0.35), (-0.25, 0.35), (-0.3, 0.3), (-0.3, -0.3)
            ]
            return outer, [hole]

        elif digit == 1:
            # Vertical line (thin rectangle) - no holes
            outer = [
                (0.1, -0.5), (0.2, -0.5), (0.2, 0.5), (0.1, 0.5),
                (0.0, 0.5), (-0.1, 0.5), (-0.1, -0.5), (0.0, -0.5)
            ]
            return outer, None

        elif digit == 2:
            # Clean "2" - curved top, angled middle, flat bottom
            outer = [
                # Top curve (left to right)
                (-0.35, -0.5), (0.35, -0.5), (0.5, -0.35),
                # Right side down
                (0.5, -0.2), (0.4, -0.05),
                # Diagonal to bottom left
                (0.3, 0.1), (-0.3, 0.35),
                # Bottom left corner
                (-0.5, 0.4), (-0.5, 0.5),
                # Bottom edge right
                (0.5, 0.5), (0.5, 0.35),
                # Inner bottom edge back
                (0.35, 0.35), (-0.2, 0.35),
                # Inner diagonal back up
                (0.2, 0.05), (0.35, -0.1),
                # Inner top curve
                (0.35, -0.3), (0.2, -0.4),
                # Top edge back left
                (-0.2, -0.4), (-0.35, -0.4)
            ]
            return outer, None

        elif digit == 3:
            # Clean "3" - two smooth curves on right
            outer = [
                # Top curve
                (-0.35, -0.5), (0.35, -0.5), (0.5, -0.35), (0.5, -0.15),
                # Upper right curve back
                (0.4, -0.05), (0.2, 0.0),
                # Middle notch left
                (-0.05, 0.0), (-0.35, -0.05),
                # Left edge
                (-0.5, -0.15), (-0.5, -0.4), (-0.4, -0.5),
                # Inner path - top
                (-0.3, -0.4), (0.25, -0.4), (0.35, -0.3), (0.35, -0.15),
                # Inner upper curve
                (0.25, -0.05), (0.1, -0.05),
                # Inner middle
                (-0.05, -0.05), (-0.05, 0.05), (0.1, 0.05),
                # Inner lower curve start
                (0.25, 0.05), (0.35, 0.15), (0.35, 0.3),
                # Inner bottom curve
                (0.25, 0.4), (-0.3, 0.4),
                # Back to outer left
                (-0.35, 0.35), (-0.35, 0.05),
                # Outer middle notch
                (-0.05, 0.05), (0.2, 0.05),
                # Lower right curve
                (0.4, 0.1), (0.5, 0.2), (0.5, 0.35),
                # Bottom
                (0.35, 0.5), (-0.35, 0.5), (-0.5, 0.4), (-0.5, 0.1)
            ]
            return outer, None

        elif digit == 4:
            # Clean "4" - open top corner
            outer = [
                # Top left vertical down
                (-0.5, -0.5), (-0.4, -0.5), (-0.4, 0.05),
                # Horizontal bar right
                (0.2, 0.05), (0.2, -0.5), (0.3, -0.5),
                # Right vertical all the way down
                (0.3, 0.5), (0.2, 0.5), (0.2, 0.15),
                # Horizontal bar inner edge back
                (-0.4, 0.15), (-0.4, 0.5), (-0.5, 0.5),
                # Left edge back up to horizontal
                (-0.5, 0.15), (0.1, 0.15), (0.1, 0.05), (-0.5, 0.05)
            ]
            return outer, None

        elif digit == 5:
            # Clean "5" - mirror of 2
            outer = [
                # Top edge full width
                (0.5, -0.5), (-0.5, -0.5), (-0.5, -0.4),
                # Left side down to middle
                (-0.5, -0.2), (-0.4, -0.05),
                # Diagonal to bottom right
                (-0.3, 0.1), (0.3, 0.35),
                # Bottom right corner
                (0.5, 0.4), (0.5, 0.5),
                # Bottom edge left
                (-0.5, 0.5), (-0.5, 0.35),
                # Inner bottom back
                (-0.35, 0.35), (0.2, 0.35),
                # Inner diagonal
                (-0.2, 0.05), (-0.35, -0.1),
                # Inner left curve
                (-0.35, -0.3), (-0.2, -0.4),
                # Top inner edge
                (0.2, -0.4), (0.35, -0.4), (0.5, -0.4)
            ]
            return outer, None

        elif digit == 6:
            # Simple outer contour wrapping the entire 6 shape
            outer = [
                # Start at top left
                (-0.3, -0.5), (0.3, -0.5), (0.35, -0.45), (0.35, -0.4),
                # Right side of stem
                (0.3, -0.35), (0.3, -0.1), (0.35, -0.05),
                # Right side of bottom loop
                (0.5, 0.0), (0.5, 0.3), (0.4, 0.4), (0.3, 0.5),
                # Bottom
                (-0.3, 0.5), (-0.4, 0.4), (-0.5, 0.3),
                # Left side all the way up
                (-0.5, -0.3), (-0.4, -0.4), (-0.35, -0.45)
            ]
            # Hole in bottom loop
            hole = [
                (-0.25, 0.05), (0.25, 0.05), (0.3, 0.1), (0.3, 0.25),
                (0.25, 0.35), (-0.25, 0.35), (-0.3, 0.25), (-0.3, 0.1)
            ]
            return outer, [hole]

        elif digit == 7:
            # Clean "7" - horizontal top with diagonal
            outer = [
                # Top edge
                (-0.4, -0.5), (0.5, -0.5), (0.5, -0.4),
                # Diagonal down to bottom
                (0.1, 0.5), (0.0, 0.5),
                # Inner diagonal back up
                (0.3, -0.35), (0.3, -0.4),
                # Inner top edge back
                (-0.4, -0.4)
            ]
            return outer, None

        elif digit == 8:
            # Two stacked circles (figure-8) with two holes
            outer = [
                # Top loop outer
                (-0.3, -0.5), (0.3, -0.5), (0.4, -0.4), (0.5, -0.3),
                (0.5, -0.15), (0.45, -0.05),
                # Transition to bottom loop
                (0.45, 0.05), (0.5, 0.15), (0.5, 0.3),
                (0.4, 0.4), (0.3, 0.5), (-0.3, 0.5),
                # Bottom loop left side
                (-0.4, 0.4), (-0.5, 0.3), (-0.5, 0.15), (-0.45, 0.05),
                # Transition back to top
                (-0.45, -0.05), (-0.5, -0.15), (-0.5, -0.3), (-0.4, -0.4)
            ]
            # Top hole
            top_hole = [
                (-0.2, -0.35), (0.2, -0.35), (0.3, -0.25), (0.3, -0.15),
                (0.2, -0.05), (-0.2, -0.05), (-0.3, -0.15), (-0.3, -0.25)
            ]
            # Bottom hole
            bottom_hole = [
                (-0.2, 0.05), (0.2, 0.05), (0.3, 0.15), (0.3, 0.25),
                (0.2, 0.35), (-0.2, 0.35), (-0.3, 0.25), (-0.3, 0.15)
            ]
            return outer, [top_hole, bottom_hole]

        elif digit == 9:
            # Simple outer contour wrapping the entire 9 shape (inverted 6)
            outer = [
                # Start at bottom left
                (-0.3, 0.5), (0.3, 0.5), (0.35, 0.45), (0.35, 0.4),
                # Right side all the way up
                (0.5, 0.3), (0.5, -0.3), (0.4, -0.4), (0.3, -0.5),
                # Top
                (-0.3, -0.5), (-0.4, -0.4), (-0.5, -0.3),
                # Left side of top loop
                (-0.5, 0.0), (-0.35, 0.05),
                # Left side of stem
                (-0.3, 0.1), (-0.3, 0.35), (-0.35, 0.4), (-0.35, 0.45)
            ]
            # Hole in top loop
            hole = [
                (-0.25, -0.35), (0.25, -0.35), (0.3, -0.25), (0.3, -0.1),
                (0.25, -0.05), (-0.25, -0.05), (-0.3, -0.1), (-0.3, -0.25)
            ]
            return outer, [hole]

        else:
            # Fallback (should never reach here due to __post_init__ validation)
            return [(-0.4, -0.5), (0.4, -0.5), (0.4, 0.5), (-0.4, 0.5)], None

    def _resample_vertices(
        self, vertices: List[Tuple[float, float]], target_count: int
    ) -> List[Tuple[float, float]]:
        """Resample vertices to match target count using linear interpolation

        Args:
            vertices: Original vertices
            target_count: Desired number of vertices

        Returns:
            Resampled vertices list with exactly target_count vertices
        """
        if len(vertices) == target_count:
            return vertices

        # Calculate cumulative distances along the path
        distances = [0.0]
        for i in range(1, len(vertices)):
            dx = vertices[i][0] - vertices[i-1][0]
            dy = vertices[i][1] - vertices[i-1][1]
            dist = (dx * dx + dy * dy) ** 0.5
            distances.append(distances[-1] + dist)

        # Add closing distance if closed path
        if self.closed:
            dx = vertices[0][0] - vertices[-1][0]
            dy = vertices[0][1] - vertices[-1][1]
            total_length = distances[-1] + (dx * dx + dy * dy) ** 0.5
        else:
            total_length = distances[-1]

        if total_length < 1e-6:
            # Degenerate path - return repeated first vertex
            return [vertices[0]] * target_count

        # Sample at regular intervals
        resampled = []
        for i in range(target_count):
            # Target distance along path
            t = i / target_count if self.closed else i / (target_count - 1)
            target_dist = t * total_length

            # Find segment containing this distance
            for j in range(len(distances) - 1):
                if distances[j] <= target_dist <= distances[j + 1]:
                    # Interpolate within this segment
                    seg_start = distances[j]
                    seg_length = distances[j + 1] - seg_start
                    if seg_length < 1e-6:
                        resampled.append(vertices[j])
                    else:
                        alpha = (target_dist - seg_start) / seg_length
                        x = vertices[j][0] * (1 - alpha) + vertices[j + 1][0] * alpha
                        y = vertices[j][1] * (1 - alpha) + vertices[j + 1][1] * alpha
                        resampled.append((x, y))
                    break
            else:
                # Handle wraparound for closed paths
                if self.closed and target_dist > distances[-1]:
                    # Interpolate between last and first vertex
                    seg_length = total_length - distances[-1]
                    if seg_length < 1e-6:
                        resampled.append(vertices[-1])
                    else:
                        alpha = (target_dist - distances[-1]) / seg_length
                        x = vertices[-1][0] * (1 - alpha) + vertices[0][0] * alpha
                        y = vertices[-1][1] * (1 - alpha) + vertices[0][1] * alpha
                        resampled.append((x, y))
                else:
                    # Edge case - append last vertex
                    resampled.append(vertices[-1])

        return resampled
