from enum import StrEnum


class ElementAlignment(StrEnum):
    """StrEnum for element alignment modes in layout functions"""

    PRESERVE = "preserve"  # Keep original rotation
    LAYOUT = "layout"  # Align with layout direction (tangent to circle, parallel to line, etc.)
    UPRIGHT = "upright"  # Start from upright position (0°)
