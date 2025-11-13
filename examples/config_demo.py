"""Demonstration of vood configuration system

This example shows how to use custom configuration to set global defaults
for scene dimensions and other properties.
"""

from vood.vscene import VScene
from vood.component import CircleState
from vood.velement import VElement
from vood.core.color import Color
from vood.config import create_config_template, get_config

# First, let's see what the default scene dimensions are
print("Default configuration:")
config = get_config()
print(f"  Scene width: {config.get('scene.width')}")
print(f"  Scene height: {config.get('scene.height')}")
print(f"  Background: {config.get('scene.background_color')}")

# Create a scene using defaults (800x800)
print("\n Creating scene with config defaults...")
scene1 = VScene()
print(f"  Created scene: {scene1.width}x{scene1.height}")

# Add a circle (using explicit colors - State classes don't use config yet)
from vood.component import CircleRenderer
circle = CircleState(
    radius=50,
    fill_color=Color("#FDBE02"),
    stroke_color=Color("#AA0000"),
    stroke_width=2
)
renderer = CircleRenderer()
element = VElement(renderer=renderer, state=circle)
scene1.add_elements([element])

# Export
from vood.vscene.vscene_exporter import VSceneExporter
exporter = VSceneExporter(scene=scene1)
exporter.export("config_demo_default", formats=["svg"])
print(f"  Exported to: output/config_demo_default.svg")

# Create a template config file for customization
print("\n To customize defaults, create a vood.toml file:")
print("  Run: python -c \"from vood.config import create_config_template; create_config_template()\"")
print("\n Example vood.toml content:")
print("""
[scene]
width = 1920
height = 1080
background_color = "#000000"
background_opacity = 1.0

[state]
# Common properties for all states
opacity = 1.0
scale = 1.0

[state.visual]
# Properties for vertex-based shapes (Circle, Ellipse, Star, etc.)
fill_color = "#FDBE02"
stroke_color = "#AA0000"
stroke_width = 2.0
""")

print("\n✓ Config demo complete!")
print("  The configuration system allows you to set global defaults")
print("  without repeating them in every VScene() call.")
