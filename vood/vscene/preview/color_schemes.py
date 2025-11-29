"""Color schemes for preview animation controls (Jupyter & dev server)"""

from dataclasses import dataclass
from typing import Dict, Optional
from vood.config import get_config, ConfigKey


@dataclass
class ColorScheme:
    """Color scheme for preview animation UI"""

    name: str
    background: str  # Container background color
    control_bg: str  # Background for buttons and controls
    control_hover: str  # Hover state for controls
    accent: str  # Accent color (play button, slider thumb)
    accent_hover: str  # Accent hover state
    text: str  # Text color
    text_muted: str  # Muted text color


# Define all available color schemes
COLOR_SCHEMES: Dict[str, ColorScheme] = {
    "vood": ColorScheme(
        name="Vood",
        background="#000017",  # Container background
        control_bg="#273141",  # Button/control backgrounds
        control_hover="#3b4553",  # Button hover state     # Play button, slider thumb
        accent="#EDAE02",
        accent_hover="#FDBE02",  # Accent hover state
        text="#f9fafb",  # Main text color
        text_muted="#9ca3af",
    ),
    "light": ColorScheme(
        name="Light",
        background="#ffffff",
        control_bg="#f5f5f5",
        control_hover="#e0e0e0",
        accent="#2563eb",
        accent_hover="#1d4ed8",
        text="#111827",
        text_muted="#6b7280",
    ),
    "dark": ColorScheme(
        name="Dark",
        background="#1f2937",
        control_bg="#374151",
        control_hover="#4b5563",
        accent="#3b82f6",
        accent_hover="#2563eb",
        text="#f9fafb",
        text_muted="#9ca3af",
    ),
    "slate": ColorScheme(
        name="Slate",
        background="#f8fafc",
        control_bg="#e2e8f0",
        control_hover="#cbd5e1",
        accent="#475569",
        accent_hover="#334155",
        text="#0f172a",
        text_muted="#64748b",
    ),
    "neutral": ColorScheme(
        name="Neutral",
        background="#fafafa",
        control_bg="#e5e5e5",
        control_hover="#d4d4d4",
        accent="#525252",
        accent_hover="#404040",
        text="#0a0a0a",
        text_muted="#737373",
    ),
    "ocean": ColorScheme(
        name="Ocean",
        background="#f0f9ff",
        control_bg="#e0f2fe",
        control_hover="#bae6fd",
        accent="#0284c7",
        accent_hover="#0369a1",
        text="#082f49",
        text_muted="#0c4a6e",
    ),
    "forest": ColorScheme(
        name="Forest",
        background="#f0fdf4",
        control_bg="#dcfce7",
        control_hover="#bbf7d0",
        accent="#16a34a",
        accent_hover="#15803d",
        text="#052e16",
        text_muted="#166534",
    ),
    "purple": ColorScheme(
        name="Purple",
        background="#faf5ff",
        control_bg="#f3e8ff",
        control_hover="#e9d5ff",
        accent="#9333ea",
        accent_hover="#7e22ce",
        text="#3b0764",
        text_muted="#6b21a8",
    ),
    "rose": ColorScheme(
        name="Rose",
        background="#fff1f2",
        control_bg="#ffe4e6",
        control_hover="#fecdd3",
        accent="#e11d48",
        accent_hover="#be123c",
        text="#4c0519",
        text_muted="#881337",
    ),
    "amber": ColorScheme(
        name="Amber",
        background="#fffbeb",
        control_bg="#fef3c7",
        control_hover="#fde68a",
        accent="#d97706",
        accent_hover="#b45309",
        text="#451a03",
        text_muted="#78350f",
    ),
    "monokai": ColorScheme(
        name="Monokai",
        background="#272822",
        control_bg="#3e3d32",
        control_hover="#49483e",
        accent="#a6e22e",
        accent_hover="#8dc731",
        text="#f8f8f2",
        text_muted="#75715e",
    ),
}


def get_color_scheme(name: Optional[str] = None) -> ColorScheme:
    """Get a color scheme by name or from config

    Priority:
    1. Explicit name parameter
    2. Individual color overrides from config
    3. Color scheme from config (preview.color_scheme)
    4. Default: "light"

    Args:
        name: Name of the color scheme (optional, uses config if not provided)

    Returns:
        ColorScheme object with config overrides applied

    Raises:
        ValueError: If color scheme name is not found
    """
    config = get_config()

    # Determine base scheme
    if name is None:
        name = config.get(ConfigKey.PREVIEW_COLOR_SCHEME, "light")

    if name not in COLOR_SCHEMES:
        available = ", ".join(COLOR_SCHEMES.keys())
        raise ValueError(f"Unknown color scheme: {name}. Available: {available}")

    base_scheme = COLOR_SCHEMES[name]

    # Apply individual color overrides from config
    return ColorScheme(
        name=base_scheme.name,
        background=config.get(ConfigKey.PREVIEW_BACKGROUND, base_scheme.background),
        control_bg=config.get(ConfigKey.PREVIEW_CONTROL_BG, base_scheme.control_bg),
        control_hover=config.get(
            ConfigKey.PREVIEW_CONTROL_HOVER, base_scheme.control_hover
        ),
        accent=config.get(ConfigKey.PREVIEW_ACCENT, base_scheme.accent),
        accent_hover=config.get(
            ConfigKey.PREVIEW_ACCENT_HOVER, base_scheme.accent_hover
        ),
        text=config.get(ConfigKey.PREVIEW_TEXT, base_scheme.text),
        text_muted=config.get(ConfigKey.PREVIEW_TEXT_MUTED, base_scheme.text_muted),
    )
