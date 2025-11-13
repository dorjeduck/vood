from enum import Enum


class ElementAlignment(Enum):
    """Enum for element alignment modes in layout functions"""

    PRESERVE = "preserve"  # Keep original rotation
    LAYOUT = "layout"  # Align with layout direction (tangent to circle, parallel to line, etc.)
    UPRIGHT = "upright"  # Start from upright position (0°)
