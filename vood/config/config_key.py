"""Configuration key enum for type-safe config access

This module defines the ConfigKey enum which provides type-safe access to all
configuration values in vood. Using enums instead of strings prevents typos
and enables better IDE autocomplete support.
"""

from enum import Enum


class ConfigKey(str, Enum):
    """Enum of all valid configuration keys in vood

    Each enum value is the dot-separated path to the config value.
    Inherits from str to maintain compatibility with string operations.

    Example:
        >>> config.get(ConfigKey.SCENE_WIDTH)
        800
        >>> config.get(ConfigKey.STATE_VISUAL_FILL_COLOR)
        Color.NONE
    """

    # Scene configuration
    SCENE_WIDTH = "scene.width"
    SCENE_HEIGHT = "scene.height"
    SCENE_BACKGROUND_COLOR = "scene.background_color"
    SCENE_BACKGROUND_OPACITY = "scene.background_opacity"
    SCENE_ORIGIN_MODE = "scene.origin_mode"

    # State base properties
    STATE_X = "state.x"
    STATE_Y = "state.y"
    STATE_SCALE = "state.scale"
    STATE_OPACITY = "state.opacity"
    STATE_ROTATION = "state.rotation"

    # State visual properties
    STATE_VISUAL_FILL_COLOR = "state.visual.fill_color"
    STATE_VISUAL_FILL_OPACITY = "state.visual.fill_opacity"
    STATE_VISUAL_STROKE_COLOR = "state.visual.stroke_color"
    STATE_VISUAL_STROKE_OPACITY = "state.visual.stroke_opacity"
    STATE_VISUAL_STROKE_WIDTH = "state.visual.stroke_width"
    STATE_VISUAL_NUM_VERTICES = "state.visual.num_vertices"
    STATE_VISUAL_CLOSED = "state.visual.closed"

    # Morphing configuration
    MORPHING_VERTEX_LOOP_MAPPER = "morphing.vertex_loop_mapper"
    MORPHING_CLUSTERING_BALANCE_CLUSTERS = "morphing.clustering.balance_clusters"
    MORPHING_CLUSTERING_MAX_ITERATIONS = "morphing.clustering.max_iterations"
    MORPHING_CLUSTERING_RANDOM_SEED = "morphing.clustering.random_seed"
    MORPHING_VERTEX_ALIGNMENT_NORM = "morphing.vertex_alignment_norm"
    MORPHING_ANGULAR_ALIGNMENT_NORM = "morphing.angular_alignment_norm"
    MORPHING_EUCLIDEAN_ALIGNMENT_NORM = "morphing.euclidean_alignment_norm"

    # Export configuration
    EXPORT_DEFAULT_FRAMERATE = "export.default_framerate"
    EXPORT_DEFAULT_CONVERTER = "export.default_converter"
    EXPORT_PNG_WIDTH_PX = "export.png_width_px"

    # Playwright server configuration
    PLAYWRIGHT_SERVER_HOST = "playwright_server.host"
    PLAYWRIGHT_SERVER_PORT = "playwright_server.port"
    PLAYWRIGHT_SERVER_AUTO_START = "playwright_server.auto_start"
    PLAYWRIGHT_SERVER_LOG_LEVEL = "playwright_server.log_level"

    # Logging configuration
    LOGGING_LEVEL = "logging.level"

    # Preview configuration (Jupyter & dev server)
    PREVIEW_COLOR_SCHEME = "preview.color_scheme"
    PREVIEW_BACKGROUND = "preview.background"
    PREVIEW_CONTROL_BG = "preview.control_bg"
    PREVIEW_CONTROL_HOVER = "preview.control_hover"
    PREVIEW_ACCENT = "preview.accent"
    PREVIEW_ACCENT_HOVER = "preview.accent_hover"
    PREVIEW_TEXT = "preview.text"
    PREVIEW_TEXT_MUTED = "preview.text_muted"

    # Dev server configuration
    DEVSERVER_PORT = "devserver.port"
    DEVSERVER_DEFAULT_FRAMES = "devserver.default_frames"
    DEVSERVER_DEFAULT_FPS = "devserver.default_fps"
    DEVSERVER_AUTO_OPEN_BROWSER = "devserver.auto_open_browser"
