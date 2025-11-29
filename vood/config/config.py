"""Configuration management for vood

This module provides a TOML-based configuration system for customizing
default values throughout vood.
"""

from __future__ import annotations
import tomllib
from pathlib import Path
from typing import Any, Optional
from copy import deepcopy

from vood.core.color import Color
from .config_key import ConfigKey


class VoodConfig:
    """Configuration manager for vood

    Loads configuration from TOML files and provides access to config values
    with proper type conversion and color normalization.

    Configuration priority (highest to lowest):
    1. User config file (if provided)
    2. System defaults (defaults.toml)
    """

    def __init__(self, config_dict: Optional[dict] = None):
        """Initialize configuration

        Args:
            config_dict: Optional pre-loaded configuration dictionary
        """
        self._config = config_dict or {}

    @classmethod
    def load_defaults(cls) -> VoodConfig:
        """Load system default configuration

        Returns:
            VoodConfig instance with system defaults
        """
        defaults_path = Path(__file__).parent / "defaults.toml"
        with open(defaults_path, "rb") as f:
            config_dict = tomllib.load(f)
        return cls(config_dict)

    @classmethod
    def load_from_file(cls, path: Path | str) -> VoodConfig:
        """Load configuration from a TOML file

        Args:
            path: Path to TOML configuration file

        Returns:
            VoodConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            tomllib.TOMLDecodeError: If TOML is invalid
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "rb") as f:
            config_dict = tomllib.load(f)

        return cls(config_dict)

    @classmethod
    def load_with_overrides(cls, user_config_path: Optional[Path | str] = None) -> VoodConfig:
        """Load defaults and override with user config if provided

        If user_config_path is None, searches for config files in standard locations:
        1. ./vood.toml (project directory)
        2. ~/.config/vood/config.toml (user config)
        3. ~/.vood.toml (user home)

        Args:
            user_config_path: Optional path to user config file

        Returns:
            VoodConfig with defaults and user overrides applied
        """
        # Load defaults
        config = cls.load_defaults()

        # Find user config if not explicitly provided
        if user_config_path is None:
            user_config_path = cls._find_user_config()

        # Apply user config if found
        if user_config_path is not None:
            try:
                user_config = cls.load_from_file(user_config_path)
                config._merge(user_config._config)
            except Exception:
                # Silently ignore missing/invalid user configs
                pass

        return config

    @staticmethod
    def _find_user_config() -> Optional[Path]:
        """Search for user config file in standard locations

        Returns:
            Path to first found config file, or None
        """
        search_paths = [
            Path.cwd() / "vood.toml",
            Path.home() / ".config" / "vood" / "config.toml",
            Path.home() / ".vood.toml",
        ]

        for path in search_paths:
            if path.exists():
                return path

        return None

    def _merge(self, other_dict: dict):
        """Recursively merge another config dict into this one

        Args:
            other_dict: Dictionary to merge (overwrites existing keys)
        """
        self._config = self._deep_merge(self._config, other_dict)

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Deep merge two dictionaries

        Args:
            base: Base dictionary
            override: Dictionary with values to override

        Returns:
            Merged dictionary
        """
        result = deepcopy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = VoodConfig._deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)

        return result

    def get(self, key: ConfigKey, default: Any = None) -> Any:
        """Get configuration value by config key enum

        Automatically normalizes color values to Color objects.

        Args:
            key: ConfigKey enum value (e.g., ConfigKey.SCENE_WIDTH)
            default: Default value if key not found

        Returns:
            Configuration value with appropriate type conversion

        Examples:
            >>> config.get(ConfigKey.SCENE_WIDTH)
            800
            >>> config.get(ConfigKey.STATE_VISUAL_FILL_COLOR)
            Color.NONE
        """
        if not isinstance(key, ConfigKey):
            raise TypeError(
                f"Config key must be a ConfigKey enum, got {type(key).__name__}. "
                f"Use ConfigKey.{key.upper().replace('.', '_')} instead of '{key}'"
            )

        path = key.value
        parts = path.split(".")
        current = self._config

        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]

        # Normalize color values
        if path.endswith("_color") or path.endswith("color"):
            return self._normalize_color(current)

        return current

    def _normalize_color(self, value: Any) -> Optional[Color]:
        """Normalize a color value to a Color object

        Args:
            value: Color value (string, tuple, list, Color object, or None)

        Returns:
            Color object or Color.NONE
        """
        if value is None:
            return Color.NONE

        if isinstance(value, Color):
            return value

        # Handle "none" string
        if isinstance(value, str) and value.lower() == "none":
            return Color.NONE

        # Handle hex color strings
        if isinstance(value, str) and value.startswith("#"):
            return Color(value)

        # Handle color name strings
        if isinstance(value, str):
            try:
                return Color(value)
            except:
                return Color.NONE

        # Handle RGB tuples/lists
        if isinstance(value, (tuple, list)):
            if len(value) == 3:
                return Color(value[0], value[1], value[2])
            elif len(value) == 4:
                # RGBA - ignore alpha for now
                return Color(value[0], value[1], value[2])

        return Color.NONE

    def set(self, key: ConfigKey, value: Any):
        """Set configuration value by config key enum

        Args:
            key: ConfigKey enum value (e.g., ConfigKey.SCENE_WIDTH)
            value: Value to set
        """
        if not isinstance(key, ConfigKey):
            raise TypeError(
                f"Config key must be a ConfigKey enum, got {type(key).__name__}. "
                f"Use ConfigKey.{key.upper().replace('.', '_')} instead of '{key}'"
            )

        path = key.value
        parts = path.split(".")
        current = self._config

        # Navigate to parent
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set value
        current[parts[-1]] = value

    def to_dict(self) -> dict:
        """Get the entire configuration as a dictionary

        Returns:
            Deep copy of configuration dictionary
        """
        return deepcopy(self._config)
