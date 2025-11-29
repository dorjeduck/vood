"""Unit tests for configuration loading and management"""

import pytest
import tomllib
from pathlib import Path
from vood.config.config import VoodConfig
from vood.config.config_key import ConfigKey
from vood.core.color import Color


@pytest.mark.unit
class TestConfigLoading:
    """Test basic configuration loading"""

    def test_load_defaults(self):
        """Test loading default configuration"""
        config = VoodConfig.load_defaults()
        assert config is not None
        assert isinstance(config.to_dict(), dict)

    def test_load_from_valid_file(self, temp_config_dir):
        """Test loading configuration from valid TOML file"""
        config_file = temp_config_dir / "test.toml"
        config_file.write_text("""
[scene]
width = 1920
height = 1080

[state]
x = 100.0
y = 200.0
""")

        config = VoodConfig.load_from_file(config_file)
        assert config._config["scene"]["width"] == 1920
        assert config._config["scene"]["height"] == 1080
        assert config._config["state"]["x"] == 100.0

    def test_load_from_missing_file_raises(self, temp_config_dir):
        """Test that loading missing file raises FileNotFoundError"""
        missing_file = temp_config_dir / "missing.toml"

        with pytest.raises(FileNotFoundError, match="Config file not found"):
            VoodConfig.load_from_file(missing_file)

    def test_load_from_malformed_toml_raises(self, temp_config_dir):
        """Test that malformed TOML raises TOMLDecodeError"""
        malformed_file = temp_config_dir / "malformed.toml"
        malformed_file.write_text("""
[scene
width = 800  # Missing closing bracket
""")

        with pytest.raises(tomllib.TOMLDecodeError):
            VoodConfig.load_from_file(malformed_file)

    def test_load_with_overrides(self, temp_config_dir):
        """Test loading with user config overrides"""
        user_config = temp_config_dir / "user.toml"
        user_config.write_text("""
[scene]
width = 2560
""")

        config = VoodConfig.load_with_overrides(user_config)

        # Should have user override
        assert config._config["scene"]["width"] == 2560

    def test_load_with_missing_user_config_uses_defaults(self):
        """Test that missing user config falls back to defaults"""
        config = VoodConfig.load_with_overrides(user_config_path="/nonexistent/path.toml")

        # Should still have defaults
        assert config is not None


@pytest.mark.unit
class TestConfigMerging:
    """Test configuration deep merging"""

    def test_merge_simple_override(self):
        """Test simple key override"""
        base_dict = {"scene": {"width": 800, "height": 600}}
        override_dict = {"scene": {"width": 1920}}

        config = VoodConfig(base_dict)
        config._merge(override_dict)

        # Width should be overridden, height preserved
        assert config._config["scene"]["width"] == 1920
        assert config._config["scene"]["height"] == 600

    def test_merge_nested_dicts(self):
        """Test deep merging of nested dictionaries"""
        base_dict = {
            "state": {
                "visual": {
                    "fill_color": "#FF0000",
                    "stroke_color": "#000000",
                    "stroke_width": 2.0
                }
            }
        }
        override_dict = {
            "state": {
                "visual": {
                    "fill_color": "#00FF00"
                }
            }
        }

        config = VoodConfig(base_dict)
        config._merge(override_dict)

        # fill_color should be overridden, others preserved
        assert config._config["state"]["visual"]["fill_color"] == "#00FF00"
        assert config._config["state"]["visual"]["stroke_color"] == "#000000"
        assert config._config["state"]["visual"]["stroke_width"] == 2.0

    def test_merge_new_keys(self):
        """Test merging adds new keys"""
        base_dict = {"scene": {"width": 800}}
        override_dict = {"scene": {"height": 600}, "export": {"framerate": 30}}

        config = VoodConfig(base_dict)
        config._merge(override_dict)

        # New keys should be added
        assert config._config["scene"]["height"] == 600
        assert config._config["export"]["framerate"] == 30
        # Original key preserved
        assert config._config["scene"]["width"] == 800

    def test_merge_replaces_non_dict_values(self):
        """Test that non-dict values are replaced, not merged"""
        base_dict = {"state": {"x": 0, "y": 0}}
        override_dict = {"state": {"x": 100}}

        config = VoodConfig(base_dict)
        config._merge(override_dict)

        assert config._config["state"]["x"] == 100
        assert config._config["state"]["y"] == 0

    def test_merge_preserves_original(self):
        """Test that merging doesn't modify original dict"""
        base_dict = {"scene": {"width": 800}}
        override_dict = {"scene": {"height": 600}}

        config = VoodConfig(base_dict)
        original_base = base_dict.copy()
        config._merge(override_dict)

        # Original should be unchanged
        assert base_dict == original_base


@pytest.mark.unit
class TestConfigGet:
    """Test configuration value retrieval"""

    def test_get_simple_value(self):
        """Test getting simple configuration value"""
        config_dict = {"scene": {"width": 1920}}
        config = VoodConfig(config_dict)

        value = config.get(ConfigKey.SCENE_WIDTH)
        assert value == 1920

    def test_get_nested_value(self):
        """Test getting nested configuration value"""
        config_dict = {"state": {"visual": {"stroke_width": 2.0}}}
        config = VoodConfig(config_dict)

        value = config.get(ConfigKey.STATE_VISUAL_STROKE_WIDTH)
        assert value == 2.0

    def test_get_missing_value_returns_default(self):
        """Test that missing value returns default"""
        config = VoodConfig({})

        value = config.get(ConfigKey.SCENE_WIDTH, default=800)
        assert value == 800

    def test_get_with_invalid_key_raises(self):
        """Test that non-ConfigKey raises TypeError"""
        config = VoodConfig({})

        with pytest.raises(TypeError, match="Config key must be a ConfigKey enum"):
            config.get("scene.width")  # String instead of enum

    def test_get_normalizes_color_strings(self):
        """Test that color values are normalized to Color objects"""
        config_dict = {"state": {"visual": {"fill_color": "#FF0000"}}}
        config = VoodConfig(config_dict)

        color = config.get(ConfigKey.STATE_VISUAL_FILL_COLOR)
        assert isinstance(color, Color)
        assert color.r == 255
        assert color.g == 0
        assert color.b == 0

    def test_get_normalizes_none_color(self):
        """Test that 'none' string is normalized to Color.NONE"""
        config_dict = {"state": {"visual": {"fill_color": "none"}}}
        config = VoodConfig(config_dict)

        color = config.get(ConfigKey.STATE_VISUAL_FILL_COLOR)
        assert color == Color.NONE


@pytest.mark.unit
class TestConfigSet:
    """Test configuration value setting"""

    def test_set_simple_value(self):
        """Test setting simple configuration value"""
        config = VoodConfig({})

        config.set(ConfigKey.SCENE_WIDTH, 1920)
        assert config._config["scene"]["width"] == 1920

    def test_set_nested_value(self):
        """Test setting nested configuration value"""
        config = VoodConfig({})

        config.set(ConfigKey.STATE_VISUAL_STROKE_WIDTH, 3.0)
        assert config._config["state"]["visual"]["stroke_width"] == 3.0

    def test_set_creates_missing_parents(self):
        """Test that setting creates missing parent dictionaries"""
        config = VoodConfig({})

        config.set(ConfigKey.STATE_VISUAL_FILL_COLOR, "#FF0000")

        # Should create nested structure
        assert "state" in config._config
        assert "visual" in config._config["state"]
        assert config._config["state"]["visual"]["fill_color"] == "#FF0000"

    def test_set_overwrites_existing_value(self):
        """Test that setting overwrites existing value"""
        config_dict = {"scene": {"width": 800}}
        config = VoodConfig(config_dict)

        config.set(ConfigKey.SCENE_WIDTH, 1920)
        assert config._config["scene"]["width"] == 1920

    def test_set_with_invalid_key_raises(self):
        """Test that non-ConfigKey raises TypeError"""
        config = VoodConfig({})

        with pytest.raises(TypeError, match="Config key must be a ConfigKey enum"):
            config.set("scene.width", 1920)  # String instead of enum


@pytest.mark.unit
class TestColorNormalization:
    """Test color value normalization"""

    def test_normalize_hex_color(self):
        """Test normalizing hex color string"""
        config = VoodConfig({})
        color = config._normalize_color("#FF0000")

        assert isinstance(color, Color)
        assert color.r == 255
        assert color.g == 0

    def test_normalize_none_string(self):
        """Test normalizing 'none' string"""
        config = VoodConfig({})
        color = config._normalize_color("none")

        assert color == Color.NONE

    def test_normalize_rgb_tuple(self):
        """Test normalizing RGB tuple"""
        config = VoodConfig({})
        color = config._normalize_color((255, 128, 64))

        assert isinstance(color, Color)
        assert color.r == 255
        assert color.g == 128
        assert color.b == 64

    def test_normalize_rgba_tuple(self):
        """Test normalizing RGBA tuple (ignores alpha)"""
        config = VoodConfig({})
        color = config._normalize_color((255, 128, 64, 128))

        assert isinstance(color, Color)
        assert color.r == 255
        assert color.g == 128
        assert color.b == 64

    def test_normalize_rgb_list(self):
        """Test normalizing RGB list"""
        config = VoodConfig({})
        color = config._normalize_color([255, 128, 64])

        assert isinstance(color, Color)
        assert color.r == 255

    def test_normalize_none_value(self):
        """Test normalizing None value"""
        config = VoodConfig({})
        color = config._normalize_color(None)

        assert color == Color.NONE

    def test_normalize_color_object(self):
        """Test normalizing existing Color object"""
        config = VoodConfig({})
        original_color = Color("#FF0000")
        color = config._normalize_color(original_color)

        assert color is original_color

    def test_normalize_invalid_color_returns_none(self):
        """Test normalizing invalid color returns Color.NONE"""
        config = VoodConfig({})
        color = config._normalize_color("invalid-color-name")

        assert color == Color.NONE


@pytest.mark.unit
class TestConfigToDictconverts():
    """Test configuration dictionary export"""

    def test_to_dict_returns_copy(self):
        """Test that to_dict returns a deep copy"""
        config_dict = {"scene": {"width": 800}}
        config = VoodConfig(config_dict)

        exported = config.to_dict()
        exported["scene"]["width"] = 1920

        # Original should be unchanged
        assert config._config["scene"]["width"] == 800

    def test_to_dict_includes_all_values(self):
        """Test that to_dict includes all configuration values"""
        config_dict = {
            "scene": {"width": 800, "height": 600},
            "state": {"x": 0, "y": 0}
        }
        config = VoodConfig(config_dict)

        exported = config.to_dict()

        assert exported["scene"]["width"] == 800
        assert exported["scene"]["height"] == 600
        assert exported["state"]["x"] == 0
        assert exported["state"]["y"] == 0


@pytest.mark.unit
class TestConfigEdgeCases:
    """Test edge cases in configuration handling"""

    def test_empty_config(self):
        """Test creating config with empty dictionary"""
        config = VoodConfig({})
        assert config.to_dict() == {}

    def test_get_from_empty_config(self):
        """Test getting value from empty config returns default"""
        config = VoodConfig({})
        value = config.get(ConfigKey.SCENE_WIDTH, default=800)
        assert value == 800

    def test_unicode_in_config(self, temp_config_dir):
        """Test handling unicode characters in config"""
        config_file = temp_config_dir / "unicode.toml"
        config_file.write_text("""
[scene]
title = "Åñîmätîöñ 動画"
""", encoding="utf-8")

        config = VoodConfig.load_from_file(config_file)
        # Should load without error

    def test_very_nested_config(self):
        """Test handling deeply nested configuration"""
        config_dict = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": 42
                        }
                    }
                }
            }
        }
        config = VoodConfig(config_dict)

        # Deep access should work
        assert config._config["level1"]["level2"]["level3"]["level4"]["value"] == 42

    def test_numeric_string_keys(self, temp_config_dir):
        """Test handling numeric string keys"""
        config_file = temp_config_dir / "numeric.toml"
        config_file.write_text("""
[scene]
"123" = 456
""")

        config = VoodConfig.load_from_file(config_file)
        assert config._config["scene"]["123"] == 456
